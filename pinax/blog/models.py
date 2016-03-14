# -*- coding: utf8 -*-
import json
try:
    from urllib2 import urlopen  # noqa
except ImportError:
    from urllib.request import urlopen  # noqa

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

from django.contrib.sites.models import Site

try:
    import twitter
except ImportError:
    twitter = None

import pytz

from .conf import settings
from .managers import PostManager
from .utils import can_tweet

try:
    from string import letters
except ImportError:
    from string import ascii_letters as letters

from random import choice


def ig(L, i):
    for x in L:
        yield x[i]

STATES = settings.PINAX_BLOG_UNPUBLISHED_STATES + ["Published"]
PINAX_BLOG_STATE_CHOICES = list(zip(range(1, 1 + len(STATES)), STATES))


@python_2_unicode_compatible
class Section(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Section")
        verbose_name_plural = _("Sections")


@python_2_unicode_compatible
class Post(models.Model):

    STATE_CHOICES = PINAX_BLOG_STATE_CHOICES

    section = models.ForeignKey(Section)

    title = models.CharField(_("Title"), max_length=90)
    slug = models.SlugField(_("Slug"), unique=settings.PINAX_BLOG_SLUG_UNIQUE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="posts", verbose_name=_("Author"))

    markup = models.CharField(_("Markup"), max_length=25, choices=settings.PINAX_BLOG_MARKUP_CHOICES)

    teaser_html = models.TextField(editable=False)
    content_html = models.TextField(editable=False)

    description = models.TextField(_("Description"), blank=True)
    primary_image = models.ForeignKey("Image", null=True, blank=True,
                                      related_name="+", verbose_name=_("Primary Image"))
    tweet_text = models.CharField(_("Tweet text"), max_length=140, editable=False)

    created = models.DateTimeField(_("Created"), default=timezone.now, editable=False)  # when first revision was created
    updated = models.DateTimeField(_("Updated"), null=True, blank=True, editable=False)  # when last revision was created (even if not published)
    published = models.DateTimeField(_("Published"), null=True, blank=True, editable=False)  # when last published
    state = models.IntegerField(_("State"), choices=STATE_CHOICES, default=STATE_CHOICES[0][0])

    secret_key = models.CharField(
        _("Secret key"),
        max_length=8,
        blank=True,
        unique=True,
        help_text=_("allows url for sharing unpublished posts to unauthenticated users")
    )

    view_count = models.IntegerField(_("View count"), default=0, editable=False)

    @property
    def older_post(self):
        qs = Post.objects.published()
        if self.is_published:
            qs = qs.filter(published__lt=self.published)
        return next(iter(qs), None)

    @property
    def newer_post(self):
        if self.is_published:
            return next(iter(Post.objects.published().order_by("published").filter(published__gt=self.published)), None)

    @property
    def is_published(self):
        return self.state == PINAX_BLOG_STATE_CHOICES[-1][0]

    @property
    def meta_description(self):
        if self.description:
            return self.description
        else:
            return strip_tags(self.teaser_html)

    @property
    def meta_image(self):
        if self.primary_image:
            return self.primary_image.image_path.url

    def rev(self, rev_id):
        return self.revisions.get(pk=rev_id)

    def current(self):
        "the currently visible (latest published) revision"
        return self.revisions.exclude(published=None).order_by("-published")[0]

    def latest(self):
        "the latest modified (even if not published) revision"
        try:
            return self.revisions.order_by("-updated")[0]
        except IndexError:
            return None

    class Meta:
        ordering = ("-published",)
        get_latest_by = "published"
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")

    objects = PostManager()

    def __str__(self):
        return self.title

    def as_tweet(self):
        if not self.tweet_text:
            current_site = Site.objects.get_current()
            api_url = "http://api.tr.im/api/trim_url.json"
            u = urlopen("%s?url=http://%s%s" % (
                api_url,
                current_site.domain,
                self.get_absolute_url(),
            ))
            result = json.loads(u.read())
            self.tweet_text = "%s %s \u2014%s" % (
                settings.TWITTER_TWEET_PREFIX,
                self.title,
                result["url"],
            )
        return self.tweet_text

    def tweet(self):
        if can_tweet():
            account = twitter.Api(
                username=settings.TWITTER_USERNAME,
                password=settings.TWITTER_PASSWORD,
            )
            account.PostUpdate(self.as_tweet())
        else:
            raise ImproperlyConfigured(
                "Unable to send tweet due to either "
                "missing python-twitter or required settings."
            )

    def save(self, **kwargs):
        self.updated_at = timezone.now()
        if not self.secret_key:
            # Generate a random secret key
            self.secret_key = "".join(choice(letters) for _ in range(8))
        if self.is_published and self.published is None:
            self.published = timezone.now()
        super(Post, self).save(**kwargs)

    @property
    def sharable_url(self):
        """
        An url to reach this post (there is a secret url for sharing unpublished
        posts to outside users).
        """
        if not self.is_published:
            if self.secret_key:
                return reverse("pinax_blog:blog_post_secret", kwargs={"post_secret_key": self.secret_key})
            else:
                return "A secret sharable url for non-authenticated users is generated when you save this post."
        else:
            return self.get_absolute_url()

    def get_absolute_url(self):
        if self.is_published:
            if settings.PINAX_BLOG_SLUG_UNIQUE:
                name = "pinax_blog:blog_post_slug"
                kwargs = {
                    "post_slug": self.slug
                }
            else:
                name = "pinax_blog:blog_post"
                if settings.USE_TZ and settings.TIME_ZONE:
                    published = pytz.timezone(settings.TIME_ZONE).normalize(self.published)
                else:
                    published = self.published
                kwargs = {
                    "year": published.strftime("%Y"),
                    "month": published.strftime("%m"),
                    "day": published.strftime("%d"),
                    "slug": self.slug,
                }
        else:
            name = "pinax_blog:blog_post_pk"
            kwargs = {
                "post_pk": self.pk,
            }
        return reverse(name, kwargs=kwargs)

    def inc_views(self):
        self.view_count += 1
        self.save()
        self.current().inc_views()


@python_2_unicode_compatible
class Revision(models.Model):

    post = models.ForeignKey(Post, related_name="revisions", verbose_name=_("Post"))

    title = models.CharField(_("Title"), max_length=90)
    teaser = models.TextField(_("Teaser"))

    content = models.TextField(_("Content"))

    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="revisions", verbose_name=_("Author"))

    updated = models.DateTimeField(_("Updated"), default=timezone.now)
    published = models.DateTimeField(_("Published"), null=True, blank=True)

    view_count = models.IntegerField(_("View count"), default=0, editable=False)

    def __str__(self):
        return _("Revision %(time)s for %(slug)s") % {'time': self.updated.strftime('%Y%m%d-%H%M'), 'slug': self.post.slug}

    def inc_views(self):
        self.view_count += 1
        self.save()

    class Meta:
        verbose_name = _("Revision")
        verbose_name_plural = _("Revisions")


@python_2_unicode_compatible
class Image(models.Model):

    post = models.ForeignKey(Post, related_name="images", verbose_name=_("Post"))

    image_path = models.ImageField(upload_to="images/%Y/%m/%d")
    url = models.CharField(_("Url"), max_length=150, blank=True)

    timestamp = models.DateTimeField(_("Timestamp"), default=timezone.now, editable=False)

    def __str__(self):
        if self.pk is not None:
            return "{{ %d }}" % self.pk
        else:
            return _("deleted image")

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")


class FeedHit(models.Model):

    request_data = models.TextField(_("Request data"))
    created = models.DateTimeField(_("Created"), default=timezone.now)


class ReviewComment(models.Model):

    post = models.ForeignKey(Post, related_name="review_comments", verbose_name=_("Post"))

    review_text = models.TextField(_("Review text"))
    timestamp = models.DateTimeField(_("Timestamp"), default=timezone.now)
    addressed = models.BooleanField(_("Addressed"), default=False)
