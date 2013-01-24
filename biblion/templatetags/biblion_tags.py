from django import template

from biblion.utils.code_hilite import to_html


register = template.Library()


register.filter("to_html", to_html)


def show_post_brief(context, post):
    return {
        "post": post,
        "last": context["forloop"]["last"],
        "can_edit": context["user"].is_staff,
    }

register.inclusion_tag("blog/post_brief.html", takes_context=True)(show_post_brief)
