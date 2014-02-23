# -*- coding: utf8 -*-
import json
try:
    from urllib2 import urlopen  # noqa
except ImportError:
    from urllib.request import urlopen  # noqa

from datetime import datetime

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django.contrib.sites.models import Site

try:
    import twitter
except ImportError:
    twitter = None

from biblion.conf import settings
from biblion.managers import PostManager
from biblion.utils import can_tweet

from string import letters
from random import choice


def ig(L, i):
    for x in L:
        yield x[i]



class Post(models.Model):

    SECTION_CHOICES = [(1, settings.BIBLION_ALL_SECTION_NAME)] + \
        zip(
            range(2, 2 + len(settings.BIBLION_SECTIONS)),
            ig(settings.BIBLION_SECTIONS, 1)
        )

    section = models.IntegerField(choices=SECTION_CHOICES)

    title = models.CharField(max_length=90)
    slug = models.SlugField()
    author = models.ForeignKey(User, related_name="posts")

    markup = models.CharField(max_length=25, choices=settings.BIBLION_MARKUP_CHOICES)

    teaser_html = models.TextField(editable=False)
    content_html = models.TextField(editable=False)

    tweet_text = models.CharField(max_length=140, editable=False)

    created = models.DateTimeField(default=datetime.now, editable=False)  # when first revision was created
    updated = models.DateTimeField(null=True, blank=True, editable=False)  # when last revision was created (even if not published)
    published = models.DateTimeField(null=True, blank=True, editable=False)  # when last published

    secret_key = models.CharField(max_length=8, blank=True) # allows url for sharing unpublished posts to unauthenticated users

    view_count = models.IntegerField(default=0, editable=False)

    @staticmethod
    def section_idx(slug):
        """
        given a slug return the index for it
        """
        if slug == settings.BIBLION_ALL_SECTION_NAME:
            return 1
        return dict(zip(ig(settings.BIBLION_SECTIONS, 0), range(2, 2 + len(settings.BIBLION_SECTIONS))))[slug]

    @property
    def section_slug(self):
        """
        an IntegerField is used for storing sections in the database so we
        need a property to turn them back into their slug form
        """
        if self.section == 1:
            return settings.BIBLION_ALL_SECTION_NAME
        return dict(zip(range(2, 2 + len(settings.BIBLION_SECTIONS)), ig(settings.BIBLION_SECTIONS, 0)))[self.section]

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
        unique_together = ("secret_key",)

    objects = PostManager()

    def __unicode__(self):
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
            self.tweet_text = "%s %s — %s" % (
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
        self.updated_at = datetime.now()
        if not self.secret_key:
            # Generate a random secret key
            self.secret_key = ''.join(choice(letters) for _ in xrange(8))
        super(Post, self).save(**kwargs)

    @property
    def sharable_url(self):
        """ An url to reach this post (there is a secret url for sharing unpublished posts to outside users).
        """
        if not self.published:
            if self.secret_key:
                return reverse("blog_post_secret", kwargs={"post_secret_key": self.secret_key})
            else:
                return "A secret sharable url for non-authenticated users is generated when you save this post."
        else:
            return self.get_absolute_url()

    def get_absolute_url(self):
        if self.published:
            name = "blog_post"
            kwargs = {
                "year": self.published.strftime("%Y"),
                "month": self.published.strftime("%m"),
                "day": self.published.strftime("%d"),
                "slug": self.slug,
            }
        else:
            name = "blog_post_pk"
            kwargs = {
                "post_pk": self.pk,
            }
        return reverse(name, kwargs=kwargs)

    def inc_views(self):
        self.view_count += 1
        self.save()
        self.current().inc_views()


class Revision(models.Model):

    post = models.ForeignKey(Post, related_name="revisions")

    title = models.CharField(max_length=90)
    teaser = models.TextField()

    content = models.TextField()

    author = models.ForeignKey(User, related_name="revisions")

    updated = models.DateTimeField(default=datetime.now)
    published = models.DateTimeField(null=True, blank=True)

    view_count = models.IntegerField(default=0, editable=False)

    def __unicode__(self):
        return "Revision %s for %s" % (self.updated.strftime('%Y%m%d-%H%M'), self.post.slug)

    def inc_views(self):
        self.view_count += 1
        self.save()


class Image(models.Model):

    post = models.ForeignKey(Post, related_name="images")

    image_path = models.ImageField(upload_to="images/%Y/%m/%d")
    url = models.CharField(max_length=150, blank=True)

    timestamp = models.DateTimeField(default=datetime.now, editable=False)

    def __unicode__(self):
        if self.pk is not None:
            return "{{ %d }}" % self.pk
        else:
            return "deleted image"


class FeedHit(models.Model):

    request_data = models.TextField()
    created = models.DateTimeField(default=datetime.now)


class ReviewComment(models.Model):

    post = models.ForeignKey(Post, related_name="review_comments")

    review_text = models.TextField()
    timestamp = models.DateTimeField(default=datetime.now)
    addressed = models.BooleanField(default=False)
