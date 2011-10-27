from datetime import datetime

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson as json
from django.views.generic import ListView, CreateView

from django.contrib.sites.models import Site

from biblion.forms import BlogForm, ImageForm, PostForm
from biblion.models import Blog, FeedHit, Section

import json



def blog_index(request, blog_slug):
    
    blog = get_object_or_404(Blog, slug=blog_slug)
    posts = blog.posts.current()
    
    return render_to_response("biblion/blog_list.html", {
        "posts": posts,
    }, context_instance=RequestContext(request))


class BlogList(ListView):
    
    model = Blog


class BlogCreate(CreateView):
    
    model = Blog
    form_class = BlogForm


def blog_post_add(request, blog_slug, **kwargs):

    blog = get_object_or_404(Blog, slug=blog_slug)
    if "slug" in kwargs:
        section = get_object_or_404(Section, slug=slug)
    else:
        section = None

    if request.method == "POST":
        form = PostForm(request.POST, blog=blog, section=section)
        if form.is_valid():
            post = form.save(request.user)
            
            if request.POST.get("next"):
                return HttpResponseRedirect(request.POST["next"])

            return HttpResponseRedirect("../%d" % post.pk)

    else:
        form = PostForm(blog=blog, section=section)

    image_form = ImageForm()

    return render_to_response("biblion/blog_post_add.html", {
        "form": form,
        "image_form": image_form,
    }, context_instance=RequestContext(request))


def blog_post_edit(request, blog_slug, post_pk, **kwargs):

    blog = get_object_or_404(Blog, slug=blog_slug)
    if "slug" in kwargs:
        section = get_object_or_404(Section, slug=slug)
    else:
        section = None

    post = get_object_or_404(blog.posts, pk=post_pk)

    if request.method == "POST":
        form = PostForm(request.POST, instance=post, blog=blog, section=section)
        if form.is_valid():
            post = form.save(request.user)

            if request.POST.get("next"):
                return HttpResponseRedirect(request.POST["next"])
            
            return HttpResponseRedirect(post.get_absolute_url())

    else:
        form = PostForm(instance=post, blog=blog, section=section)

    image_form = ImageForm()

    return render_to_response("biblion/blog_post_edit.html", {
        "form": form,
        "image_form": image_form,
        "post": post,
    }, context_instance=RequestContext(request))


def blog_image_upload(request, **kwargs):

    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save()
            response = {
                "status": "success", 
                "height": image.image_path.height,
                "width": image.image_path.width,
                "src": image.image_path.url,
                "pk": image.pk,
            }
        else:
            response = {
                "status": "error",
            }
        return HttpResponse(json.dumps(response), mimetype="application/json")
    
    return Http404


def blog_section_list(request, blog_slug, slug):
    
    blog = get_object_or_404(Blog, slug=blog_slug)
    section = get_object_or_404(Section, slug=slug)
    posts = blog.posts.filter(section=section)
    
    return render_to_response("biblion/blog_section_list.html", {
        "section_slug": slug,
        "section_name": section.name,
        "posts": posts,
    }, context_instance=RequestContext(request))


def blog_post_detail(request, **kwargs):
    
    blog = get_object_or_404(Blog, slug=kwargs["blog_slug"])
    
    if "post_pk" in kwargs:
        if request.user.is_authenticated() and request.user.is_staff:
            queryset = blog.posts.all()
            post = get_object_or_404(queryset, pk=kwargs["post_pk"])
        else:
            raise Http404()
    else:
        queryset = blog.posts.current()
        queryset = queryset.filter(
            published__year = int(kwargs["year"]),
            published__month = int(kwargs["month"]),
            published__day = int(kwargs["day"]),
        )
        post = get_object_or_404(queryset, slug=kwargs["slug"])
        post.inc_views()
    
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


def blog_feed(request, blog_slug, slug=None):
    
    blog = get_object_or_404(Blog, slug=blog_slug)
    
    if slug:
        section = get_object_or_404(Section, slug=slug)
        posts = blog.posts.filter(section=section)
    else:
        section = Section.objects.get(slug="all")
        posts = blog.posts()
    
    current_site = Site.objects.get_current()
    
    feed_title = "%s Blog: %s" % (current_site.name, section.blog.title.upper() + section.name)
    
    blog_url = "http://%s%s" % (current_site.domain, reverse("blog"))
    
    url_name, kwargs = "blog_feed", {"section": section.slug}
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
