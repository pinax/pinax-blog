# -*- coding: utf8 -*-
import urllib2

from datetime import datetime

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils import simplejson as json

from django.contrib.sites.models import Site

try:
    import twitter
except ImportError:
    twitter = None

from biblion.managers import PostManager
from biblion.utils import can_tweet


class Blog(models.Model):
    
    title = models.CharField(max_length=128)
    subtitle = models.CharField(max_length=256, null=True, blank=True)
    slug = models.SlugField()
    
    def __unicode__(self):
        return unicode(self.title)
    
    def get_absolute_url(self):
        return reverse("blog", kwargs={"blog_slug": self.slug})


class Section(models.Model):
    
    blog = models.ForeignKey(Blog, related_name="sections")
    name = models.CharField(max_length=128)
    slug = models.SlugField()
    
    def __unicode__(self):
        return u"%s - %s" % (self.blog, self.name)


class Post(models.Model):
    
    blog = models.ForeignKey(Blog, related_name="posts")
    section = models.ForeignKey(Section, related_name="posts", blank=True, null=True)
    
    title = models.CharField(max_length=90)
    slug = models.SlugField()
    author = models.ForeignKey(User, related_name="posts")
    
    teaser_html = models.TextField(editable=False)
    content_html = models.TextField(editable=False)
    
    tweet_text = models.CharField(max_length=140, editable=False)
    
    created = models.DateTimeField(default=datetime.now, editable=False) # when first revision was created
    updated = models.DateTimeField(null=True, blank=True, editable=False) # when last revision was create (even if not published)
    published = models.DateTimeField(null=True, blank=True, editable=False) # when last published
    
    view_count = models.IntegerField(default=0, editable=False)
    
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
                username = settings.TWITTER_USERNAME,
                password = settings.TWITTER_PASSWORD,
            )
            account.PostUpdate(self.as_tweet())
        else:
            raise ImproperlyConfigured("Unable to send tweet due to either "
                "missing python-twitter or required settings.")
    
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
    
    def inc_views(self):
        self.view_count += 1
        self.save()
        self.current().inc_views()


class Revision(models.Model):
    
    post = models.ForeignKey(Post, related_name="revisions")
    
    title = models.CharField(max_length=90)
    teaser = models.TextField()
    
    content = models.TextField()
    
    author = models.ForeignKey(User, related_name="post_revisions")
    
    updated = models.DateTimeField(default=datetime.now)
    published = models.DateTimeField(null=True, blank=True)
    
    view_count = models.IntegerField(default=0, editable=False)
    
    def __unicode__(self):
        return 'Revision %s for %s' % (self.updated.strftime('%Y%m%d-%H%M'), self.post.slug)
    
    def inc_views(self):
        self.view_count += 1
        self.save()


class Image(models.Model):
    
    post = models.ForeignKey(Post, related_name="images", blank=True, null=True)
    
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

