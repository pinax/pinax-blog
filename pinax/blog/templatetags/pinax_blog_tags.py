from django import template

from ..models import Post, Section


register = template.Library()


@register.assignment_tag
def latest_blog_posts(scoped_for=None):
    qs = Post.objects.current()
    if scoped_for:
        qs = qs.filter(scoped_for=scoped_for)
    return qs[:5]


@register.assignment_tag
def latest_blog_post(scoped_for=None):
    qs = Post.objects.current()
    if scoped_for:
        qs = qs.filter(scoped_for=scoped_for)
    return qs[0]


@register.assignment_tag
def latest_section_post(section, scoped_for=None):
    qs = Post.objects.published().filter(section__name=section).order_by("-published")
    if scoped_for:
        qs = qs.filter(scoped_for=scoped_for)
    return qs[0] if qs.count() > 0 else None


@register.assignment_tag
def blog_sections():
    return Section.objects.filter(enabled=True)
