import json

from datetime import datetime

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, DeleteView, CreateView, UpdateView
from django.views.generic.dates import DateDetailView

from django.contrib.sites.models import Site

from .conf import settings
from .forms import PostForm
from .hooks import hookset
from .managers import PUBLISHED_STATE
from .models import Post, FeedHit, Section
from .signals import post_viewed, post_redirected
from .parsers.markdown_parser import parse


class BlogIndexView(ListView):
    model = Post
    template_name = "pinax/blog/blog_list.html"
    search_parameter = "q"
    paginate_by = settings.PINAX_BLOG_PAGINATE_BY

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
        blog = hookset.get_blog(**self.kwargs)
        qs = Post.objects.current().filter(blog=blog)
        return self.search(qs)


class SectionIndexView(BlogIndexView):

    def get_current_section(self):
        section = get_object_or_404(Section, slug__iexact=self.kwargs.get("section"))
        return section

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
        blog = hookset.get_blog(**self.kwargs)
        return super(SlugUniquePostDetailView, self).get_queryset().filter(
            blog=blog,
            state=PUBLISHED_STATE
        )


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
        blog = hookset.get_blog(**self.kwargs)
        return super(DateBasedPostDetailView, self).get_queryset().filter(
            blog=blog,
            state=PUBLISHED_STATE
        )


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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_published and not self.object.is_future_published:
            return redirect(self.object.get_absolute_url())
        return super(SecretKeyPostDetailView, self).get(request, *args, **kwargs)


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


def blog_feed(request, **kwargs):

    section = kwargs.get("section", None)
    feed_type = kwargs.get("feed_type", None)
    scoper_lookup = kwargs.get(settings.PINAX_BLOG_SCOPING_URL_VAR, None)

    blog = hookset.get_blog(**kwargs)
    posts = Post.objects.published().filter(blog=blog).order_by("-updated")

    blog_url_kwargs = {}
    if scoper_lookup is not None:
        blog_url_kwargs = {settings.PINAX_BLOG_SCOPING_URL_VAR: scoper_lookup}

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
    feed_url_kwargs = {"section": section.slug if section != "all" else "all", "feed_type": feed_type}
    feed_url_kwargs.update(blog_url_kwargs)
    blog_url = "http://%s%s" % (current_site.domain, reverse("pinax_blog:blog", kwargs=blog_url_kwargs))
    feed_url = "http://%s%s" % (current_site.domain, reverse("pinax_blog:blog_feed", kwargs=feed_url_kwargs))

    if posts:
        feed_updated = posts[0].updated
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


class ManageBlogMixin(object):

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        if hookset.can_manage(request, *args, **kwargs):
            self.blog = hookset.get_blog(**kwargs)
            return super(ManageBlogMixin, self).dispatch(request, *args, **kwargs)
        return hookset.response_cannot_manage(request, *args, **kwargs)


class ManageSuccessUrlMixin(object):

    def get_success_url(self):
        scoping_lookup = self.kwargs.get(settings.PINAX_BLOG_SCOPING_URL_VAR, None)
        if scoping_lookup:
            return reverse("pinax_blog:manage_post_list", kwargs={settings.PINAX_BLOG_SCOPING_URL_VAR: scoping_lookup})
        return reverse("pinax_blog:manage_post_list")


class ManagePostList(ManageBlogMixin, ListView):

    model = Post
    template_name = "pinax/blog/manage_post_list.html"

    def get_queryset(self):
        return super(ManagePostList, self).get_queryset().filter(blog=self.blog)


class ManageCreatePost(ManageBlogMixin, ManageSuccessUrlMixin, CreateView):

    model = Post
    form_class = PostForm
    template_name = "pinax/blog/manage_post_create.html"

    def form_valid(self, form):
        form.save(blog=self.blog, author=self.request.user)
        return redirect(self.get_success_url())


class ManageUpdatePost(ManageBlogMixin, ManageSuccessUrlMixin, UpdateView):

    model = Post
    form_class = PostForm
    pk_url_kwarg = "post_pk"
    template_name = "pinax/blog/manage_post_update.html"

    def get_queryset(self):
        return super(ManageUpdatePost, self).get_queryset().filter(blog=self.blog)


class ManageDeletePost(ManageBlogMixin, ManageSuccessUrlMixin, DeleteView):

    model = Post
    pk_url_kwarg = "post_pk"
    template_name = "pinax/blog/manage_post_delete_confirm.html"

    def get_queryset(self):
        return super(ManageDeletePost, self).get_queryset().filter(blog=self.blog)


@require_POST
def ajax_preview(request, **kwargs):
    """
    Currently only supports markdown
    """
    data = {
        "html": render_to_string("pinax/blog/_preview.html", {
            "content": parse(request.POST.get("markup"))
        })
    }
    return JsonResponse(data)
