import json

from datetime import datetime

from django.db.models import Q
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string

from django.contrib.sites.models import Site

from biblion.conf import settings
from biblion.exceptions import InvalidSection
from biblion.models import Post, FeedHit
from biblion.signals import post_viewed, post_redirected


def blog_index(request):

    posts = Post.objects.current()

    if request.GET.get("q"):
        posts = posts.filter(
            Q(title__icontains=request.GET.get("q")) |
            Q(teaser_html__icontains=request.GET.get("q")) |
            Q(content_html__icontains=request.GET.get("q"))
        )
        if posts.count() == 1:
            return redirect(posts.get().get_absolute_url())

    return render_to_response("biblion/blog_list.html", {
        "posts": posts,
        "search_term": request.GET.get("q")
    }, context_instance=RequestContext(request))


def blog_section_list(request, section):

    try:
        posts = Post.objects.section(section)
    except InvalidSection:
        raise Http404()

    return render_to_response("biblion/blog_section_list.html", {
        "section_slug": section,
        "section_name": dict(Post.SECTION_CHOICES)[Post.section_idx(section)],
        "posts": posts,
    }, context_instance=RequestContext(request))


def blog_post_detail(request, **kwargs):

    if "post_pk" in kwargs:
        if request.user.is_authenticated() and request.user.is_staff:
            queryset = Post.objects.all()
            post = get_object_or_404(queryset, pk=kwargs["post_pk"])
        else:
            raise Http404()
    elif "post_secret_key" in kwargs:
        post = get_object_or_404(Post, secret_key=kwargs["post_secret_key"])
    else:
        queryset = Post.objects.current()
        if "post_slug" in kwargs:
            if not settings.BIBLION_SLUG_UNIQUE:
                raise Http404()
            post = get_object_or_404(queryset, slug=kwargs["post_slug"])
        else:
            queryset = queryset.filter(
                published__year=int(kwargs["year"]),
                published__month=int(kwargs["month"]),
                published__day=int(kwargs["day"]),
            )
            post = get_object_or_404(queryset, slug=kwargs["slug"])
            if settings.BIBLION_SLUG_UNIQUE:
                post_redirected.send(sender=post, post=post, request=request)
                return redirect(post.get_absolute_url(), permanent=True)
        post_viewed.send(sender=post, post=post, request=request)

    return render_to_response("biblion/blog_post.html", {
        "post": post,
    }, context_instance=RequestContext(request))


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

    try:
        posts = Post.objects.section(section)
    except InvalidSection:
        raise Http404()

    if section is None:
        section = settings.BIBLION_ALL_SECTION_NAME

    if feed_type == "atom":
        feed_template = "biblion/atom_feed.xml"
        feed_mimetype = "application/atom+xml"
    elif feed_type == "rss":
        feed_template = "biblion/rss_feed.xml"
        feed_mimetype = "application/rss+xml"
    else:
        raise Http404()

    current_site = Site.objects.get_current()

    feed_title = "%s Blog: %s" % (current_site.name, section[0].upper() + section[1:])

    blog_url = "http://%s%s" % (current_site.domain, reverse("blog"))

    url_name, kwargs = "blog_feed", {"section": section, "feed_type": feed_type}
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
