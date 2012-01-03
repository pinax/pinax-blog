# -*- coding: utf-8 -*-
import urllib2

from datetime import datetime

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.core.urlresolvers import reverse
from django.utils import simplejson as json
from django.utils.translation import ugettext as _

from django.contrib.auth.models import User
from django.contrib.sites.models import Site

try:
    import twitter
except ImportError:
    twitter = None

from biblion.managers import PostManager
from biblion.utils.twitter import can_tweet


class Biblion(models.Model):
    
    title = models.CharField(_("title"), max_length=128)
    subtitle = models.CharField(_("subtitle"), max_length=256, blank=True)
    slug = models.SlugField(_("slug"), unique=True)
    description = models.TextField(_("description"), verbose_name)
    logo = models.FileField(_("logo"), upload_to="biblion_biblion_logo")
    sites = models.ManyToManyField(Site, verbose_name=_("list of sites"))
    
    class Meta:
        verbose_name = _("biblion")
        verbose_name_plural = _("biblia")
    
    def __unicode__(self):
        return unicode(self.title)
    
    def get_absolute_url(self):
        return reverse("biblion_detail", kwargs={"slug": self.slug})


class BiblionContributor(models.Model):
    
    biblion = models.ForeignKey(Biblion, verbose_name=_("biblion"))
    user = models.ForeignKey(User, related_name="contributors", verbose_name=_("user"))
    role = models.CharField(_("role"), max_length=25)
    
    class Meta:
        verbose_name = _("biblion contributor")
        verbose_name_plural = _("biblion contributors")


class Post(models.Model):
    
    biblion = models.ForeignKey(Biblion, related_name="posts", verbose_name=_("biblion"))
    sites = models.ManyToManyField(Site, verbose_name=_("list of sites"))
    
    title = models.CharField(_("title"), max_length=90)
    slug = models.SlugField(_("slug"))
    author = models.ForeignKey(User, related_name="posts", verbose_name=_("author"))
    
    markup_types = [
        _("HTML"),
        _("Creole"),
        _("Markdown"),
        _("reStructuredText")
        _("Textile")
    ]
    MARKUP_CHOICES = zip(range(1, 1 + len(markup_types)), markup_types)
    markup_type = models.IntegerField(_("markup_type"), choices=MARKUP_CHOICES, default=1)
    
    teaser = models.TextField(_("teaser"), editable=False)
    content = models.TextField(_("content"), editable=False)
    
    tweet_text = models.CharField(_("tweet_text"), max_length=140, editable=False)
    
    created = models.DateTimeField(_("created"), default=datetime.now, editable=False) # when first revision was created
    updated = models.DateTimeField(_("updated"), null=True, blank=True, editable=False) # when last revision was created (even if not published)
    published = models.DateTimeField(_("published"), null=True, blank=True, editable=False) # when last published
    
    view_count = models.IntegerField(_("view_count"), default=0, editable=False)
    
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
        verbose_name = _("post")
        verbose_name_plural = _("posts")
        ordering = ("-published",)
        get_latest_by = "published"
    
    objects = PostManager()
    
    def __unicode__(self):
        return self.title
    
    def as_tweet(self):
        if not self.tweet_text:
            current_site = Site.objects.get_current()
            api_url = "http://api.tr.im/api/trim_url.json"
            u = urllib2.urlopen("%s?url=http://%s%s" % (
                api_url,
                current_site.domain,
                self.get_absolute_url(),
            ))
            result = json.loads(u.read())
            self.tweet_text = u"%s %s — %s" % (
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
            raise ImproperlyConfigured(_("Unable to send tweet due to either \
                missing python-twitter or required settings."))
    
    def save(self, **kwargs):
        self.updated_at = datetime.now()
        super(Post, self).save(**kwargs)
    
    def get_absolute_url(self):
        if self.published and datetime.now() > self.published:
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
        kwargs.update({"blog_slug": self.blog.slug})
        return reverse(name, kwargs=kwargs)
    
    def get_absolute_url(self):
        return reverse("biblion_post_detail", kwargs={"slug": self.slug})
    
    def inc_views(self):
        self.view_count += 1
        self.save()
        self.current().inc_views()


class Revision(models.Model):
    
    post = models.ForeignKey(Post, related_name="revisions", verbose_name=_("post"))
    
    title = models.CharField(_("title"), max_length=90)
    
    markup_type = models.IntegerField(_("markup_type"))
    teaser = models.TextField(_("teaser"))
    content = models.TextField(_("content"))
    
    author = models.ForeignKey(User, related_name="post_revisions", verbose_name=_("author"))
    
    updated = models.DateTimeField(_("updated"), default=datetime.now)
    published = models.DateTimeField(_("published"), null=True, blank=True)
    
    view_count = models.IntegerField(_("view_count"), default=0, editable=False)
    
    class Meta:
        verbose_name = _("revision")
        verbose_name_plural = _("revisions")
    
    def __unicode__(self):
        return _("Revision %(datetime)s for %(slug)s") % {
                     "datetime": self.updated.strftime("%Y%m%d-%H%M"),
                     "slug": self.post.slug}
    
    def inc_views(self):
        self.view_count += 1
        self.save()


class Image(models.Model):
    
    post = models.ForeignKey(Post, related_name="images", blank=True, null=True)
    
    image_path = models.ImageField(_("image_path"), upload_to="images/%Y/%m/%d")
    url = models.CharField(_("url"), max_length=150, blank=True)
    
    timestamp = models.DateTimeField(_("timestamp"), default=datetime.now, editable=False)
    
    class Meta:
        verbose_name = _("image")
        verbose_name_plural = _("images")
    
    def __unicode__(self):
        if self.pk is not None:
            return u"{{ %d }}" % self.pk
        else:
            return _("deleted image")


class FeedHit(models.Model):
    
    request_data = models.TextField(_("request_data"))
    created = models.DateTimeField(_("created"), default=datetime.now)
