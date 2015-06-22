import json

from datetime import datetime

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import DetailView, ListView
from django.views.generic.dates import DateDetailView

from django.contrib.sites.models import Site

from .conf import settings
from .managers import PUBLISHED_STATE
from .models import Post, FeedHit, Section
from .signals import post_viewed, post_redirected


class BlogIndexView(ListView):
    model = Post
    template_name = "pinax/blog/blog_list.html"
    search_parameter = "q"
    paginate_by = 10

    def get_current_section(self):
        return "all"

    def get_context_data(self, **kwargs):
        context = super(BlogIndexView, self).get_context_data(**kwargs)
        context.update({
            "current_section": self.get_current_section(),
            "search_term": self.search_term()
        })
        return context

    def search_term(self):
        return self.request.GET.get(self.search_parameter)

    def search(self, posts):
        q = self.search_term()
        if q:
            posts = posts.filter(
                Q(title__icontains=q) |
                Q(teaser_html__icontains=q) |
                Q(content_html__icontains=q)
            )
        return posts

    def get_queryset(self):
        return self.search(Post.objects.current())


class SectionIndexView(BlogIndexView):

    def get_current_section(self):
        return Section.objects.get(slug__iexact=self.kwargs.get("section"))

    def get_queryset(self):
        queryset = super(SectionIndexView, self).get_queryset()
        queryset = queryset.filter(section__slug__iexact=self.kwargs.get("section"))
        return queryset


class SlugUniquePostDetailView(DetailView):
    model = Post
    template_name = "pinax/blog/blog_post.html"
    slug_url_kwarg = "post_slug"

    def get(self, request, *args, **kwargs):
        if not settings.PINAX_BLOG_SLUG_UNIQUE:
            raise Http404()
        self.object = self.get_object()
        context = self.get_context_data(object=self.object, current_section=self.object.section)
        post_viewed.send(sender=self.object, post=self.object, request=request)
        return self.render_to_response(context)

    def get_queryset(self):
        queryset = super(SlugUniquePostDetailView, self).get_queryset()
        queryset = queryset.filter(state=PUBLISHED_STATE)
        return queryset


class DateBasedPostDetailView(DateDetailView):
    model = Post
    month_format = "%m"
    date_field = "published"
    template_name = "pinax/blog/blog_post.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if settings.PINAX_BLOG_SLUG_UNIQUE:
            post_redirected.send(sender=self.object, post=self.object, request=request)
            return redirect(self.object.get_absolute_url(), permanent=True)
        context = self.get_context_data(object=self.object, current_section=self.object.section)
        post_viewed.send(sender=self.object, post=self.object, request=request)
        return self.render_to_response(context)

    def get_queryset(self):
        queryset = super(DateBasedPostDetailView, self).get_queryset()
        queryset = queryset.filter(state=PUBLISHED_STATE)
        return queryset


class StaffPostDetailView(DetailView):
    model = Post
    template_name = "pinax/blog/blog_post.html"
    pk_url_kwarg = "post_pk"

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated() and not request.user.is_staff:
            raise Http404()
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class SecretKeyPostDetailView(DetailView):
    model = Post
    slug_url_kwarg = "post_secret_key"
    slug_field = "secret_key"
    template_name = "pinax/blog/blog_post.html"


def serialize_request(request):
    data = {
        "path": request.path,
        "META": {
            "QUERY_STRING": request.META.get("QUERY_STRING"),
            "REMOTE_ADDR": request.META.get("REMOTE_ADDR"),
        }
    }
    for key in request.META:
        if key.startswith("HTTP"):
            data["META"][key] = request.META[key]
    return json.dumps(data)


def blog_feed(request, section=None, feed_type=None):

    posts = Post.objects.current()
    if section and section != "all":
        section = get_object_or_404(Section, slug=section)
        feed_title = settings.PINAX_BLOG_SECTION_FEED_TITLE % section.name
        posts = posts.filter(section=section)
    else:
        feed_title = settings.PINAX_BLOG_FEED_TITLE
        section = settings.PINAX_BLOG_ALL_SECTION_NAME

    if feed_type == "atom":
        feed_template = "pinax/blog/atom_feed.xml"
        feed_mimetype = "application/atom+xml"
    elif feed_type == "rss":
        feed_template = "pinax/blog/rss_feed.xml"
        feed_mimetype = "application/rss+xml"
    else:
        raise Http404()

    current_site = Site.objects.get_current()
    blog_url = "http://%s%s" % (current_site.domain, reverse("blog"))
    url_name, kwargs = "blog_feed", {"section": section.slug if section != "all" else "all", "feed_type": feed_type}
    feed_url = "http://%s%s" % (current_site.domain, reverse(url_name, kwargs=kwargs))

    if posts:
        feed_updated = posts[0].published
    else:
        feed_updated = datetime(2009, 8, 1, 0, 0, 0)

    # create a feed hit
    hit = FeedHit()
    hit.request_data = serialize_request(request)
    hit.save()

    feed = render_to_string(feed_template, {
        "feed_id": feed_url,
        "feed_title": feed_title,
        "blog_url": blog_url,
        "feed_url": feed_url,
        "feed_updated": feed_updated,
        "entries": posts,
        "current_site": current_site,
    })
    return HttpResponse(feed, content_type=feed_mimetype)
