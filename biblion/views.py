import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson as json
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site

from biblion.forms import BiblionForm, ImageForm, PostForm
from biblion.models import Biblion, Post, FeedHit


class BiblionList(ListView):
    
    model = Biblion
    
    def get_queryset(self):
        return Biblion.objects.filter(sites=settings.SITE_ID)


class BiblionCreate(CreateView):
    
    model = Biblion
    form_class = BiblionForm
    template_name_suffix = "_create"
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BiblionCreate, self).dispatch(*args, **kwargs)


class BiblionUpdate(UpdateView):
    
    model = Biblion
    form_class = BiblionForm
    template_name_suffix = "_update"
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BiblionUpdate, self).dispatch(*args, **kwargs)


class BiblionDetail(DetailView):
    
    model = Biblion


class PostCreate(CreateView):
    
    model = Post
    form_class = PostForm
    template_name_suffix = "_create"
    
    def get_form_kwargs(self):
        kwargs = super(PostCreate, self).get_form_kwargs()
        kwargs.update({
            "biblion": self.biblion,
            "user": self.request.user,
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        ctx = super(PostCreate, self).get_context_data(**kwargs)
        ctx.update({
            "biblion": self.biblion,
        })
        return ctx
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.biblion = get_object_or_404(Biblion, slug=kwargs["slug"])
        return super(PostCreate, self).dispatch(*args, **kwargs)


class PostUpdate(UpdateView):
    
    model = Post
    form_class = PostForm
    template_name_suffix = "_update"
    
    def get_form_kwargs(self):
        kwargs = super(PostUpdate, self).get_form_kwargs()
        kwargs.update({
            "biblion": self.biblion,
            "user": self.request.user,
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        ctx = super(PostUpdate, self).get_context_data(**kwargs)
        ctx.update({
            "biblion": self.biblion,
        })
        return ctx
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        post = get_object_or_404(Post, slug=kwargs["slug"])
        self.biblion = post.biblion
        return super(PostUpdate, self).dispatch(*args, **kwargs)


class PostDetail(DetailView):
    
    model = Post
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Post.objects.filter(sites=settings.SITE_ID)
        return Post.objects.current()


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


def blog_feed(request, biblion_slug):
    
    biblion = get_object_or_404(Biblion, slug=biblion_slug)
    posts = biblion.posts()
    
    current_site = Site.objects.get_current()
    
    feed_title = "%s Blog" % current_site.name
    
    blog_url = "http://%s%s" % (current_site.domain, reverse("blog"))
    
    url_name, kwargs = "blog_feed", {}
    feed_url = "http://%s%s" % (current_site.domain, reverse(url_name, kwargs=kwargs))
    
    if posts:
        feed_updated = posts[0].published
    else:
        feed_updated = datetime.datetime(2009, 8, 1, 0, 0, 0)
    
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
