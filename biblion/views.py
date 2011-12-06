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


def blog_index(request, biblion_slug):
    
    biblion = get_object_or_404(Biblion, slug=biblion_slug)
    posts = biblion.posts.current()
    
    return render_to_response("biblion/blog_list.html", {
        "posts": posts,
    }, context_instance=RequestContext(request))


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
    template_name = "biblion/post_update.html"
    
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


def blog_post_add(request, blog_slug, post_form=PostForm, **kwargs):
    
    blog = get_object_or_404(Blog, slug=blog_slug)
    if "slug" in kwargs:
        section = get_object_or_404(Section, slug=kwargs.get("slug"))
    else:
        section = None
    
    if request.method == "POST":
        form = post_form(request.POST, blog=blog, section=section, user=request.user)
        if form.is_valid():
            post = form.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                ugettext("The post '%s' was successfully created." % post.title)
            )
            if request.POST.get("next"):
                return HttpResponseRedirect(request.POST["next"])
            
            return HttpResponseRedirect(post.get_absolute_url())
    
    else:
        form = post_form(blog=blog, section=section, user=request.user)
    
    image_form = ImageForm()
    
    return render_to_response("biblion/blog_post_add.html", {
        "blog": blog,
        "form": form,
        "image_form": image_form,
    }, context_instance=RequestContext(request))


def blog_post_edit(request, blog_slug, post_pk, post_form=PostForm, **kwargs):
    
    blog = get_object_or_404(Blog, slug=blog_slug)
    if "slug" in kwargs:
        section = get_object_or_404(Section, kwargs.get("slug"))
    else:
        section = None
    
    post = get_object_or_404(blog.posts, pk=post_pk)
    
    if request.method == "POST":
        
        form = post_form(request.POST, instance=post, blog=blog, section=section, user=request.user)
        if form.is_valid():
            post = form.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                ugettext("The post '%s' was successfully updated." % post.title)
            )
            if request.POST.get("next"):
                return HttpResponseRedirect(request.POST["next"])
            
            return HttpResponseRedirect(post.get_absolute_url())
    
    else:
        form = post_form(instance=post, blog=blog, section=section, user=request.user)
    
    image_form = ImageForm()
    
    return render_to_response("biblion/blog_post_edit.html", {
        "blog": blog,
        "form": form,
        "image_form": image_form,
        "post": post,
    }, context_instance=RequestContext(request))


def blog_post_delete(request, blog_slug, post_pk, **kwargs):
    
    blog = get_object_or_404(Blog, slug=blog_slug)
    post = get_object_or_404(blog.posts, pk=post_pk)
    
    if request.method == "POST":
        post.delete()
        return HttpResponseRedirect(request.POST.get("next") or "/")
    
    return render_to_response("biblion/blog_post_delete.html", {
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


def blog_post_detail(request, **kwargs):
    
    biblion = get_object_or_404(Biblion, slug=kwargs["biblion_slug"])
    
    if "post_pk" in kwargs:
        if not (request.user.is_authenticated() and request.user.is_staff) and post.author != request.user:
            raise Http404()
        else:
            queryset = biblion.posts.all()
            post = get_object_or_404(queryset, pk=kwargs["post_pk"])
    else:
        queryset = biblion.posts.current()
        queryset = queryset.filter(
            published__year = int(kwargs["year"]),
            published__month = int(kwargs["month"]),
            published__day = int(kwargs["day"]),
        )
        post = get_object_or_404(queryset, slug=kwargs["slug"])
        post.inc_views()
    
    return render_to_response("biblion/blog_post.html", {
        "blog": blog,
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
