from datetime import datetime

from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson as json

from django.contrib.sites.models import Site

from biblion.exceptions import InvalidSection
from biblion.models import Post, FeedHit
from biblion.settings import ALL_SECTION_NAME
from biblion.signals import post_viewed


def blog_index(request):
    
    posts = Post.objects.current()
    
    return render_to_response("biblion/blog_list.html", {
        "posts": posts,
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
    else:
        queryset = Post.objects.current()
        queryset = queryset.filter(
            published__year = int(kwargs["year"]),
            published__month = int(kwargs["month"]),
            published__day = int(kwargs["day"]),
        )
        post = get_object_or_404(queryset, slug=kwargs["slug"])
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


def blog_feed(request, section=None):
    
    try:
        posts = Post.objects.section(section)
    except InvalidSection:
        raise Http404()
    
    if section is None:
        section = ALL_SECTION_NAME
    
    current_site = Site.objects.get_current()
    
    feed_title = "%s Blog: %s" % (current_site.name, section[0].upper() + section[1:])
    
    blog_url = "http://%s%s" % (current_site.domain, reverse("blog"))
    
    url_name, kwargs = "blog_feed", {"section": section}
    feed_url = "http://%s%s" % (current_site.domain, reverse(url_name, kwargs=kwargs))
    
    if posts:
        feed_updated = posts[0].published
    else:
        feed_updated = datetime(2009, 8, 1, 0, 0, 0)
    
    # create a feed hit
    hit = FeedHit()
    hit.request_data = serialize_request(request)
    hit.save()
    
    atom = render_to_string("biblion/atom_feed.xml", {
        "feed_id": feed_url,
        "feed_title": feed_title,
        "blog_url": blog_url,
        "feed_url": feed_url,
        "feed_updated": feed_updated,
        "entries": posts,
        "current_site": current_site,
    })
    return HttpResponse(atom, mimetype="application/atom+xml")
