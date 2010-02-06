from django import template

from biblion.models import Post
from biblion.settings import ALL_SECTION_NAME, SECTIONS


register = template.Library()


class LatestBlogPostsNode(template.Node):
    
    def __init__(self, context_var):
        self.context_var = context_var
    
    def render(self, context):
        latest_posts = Post.objects.current()[:5]
        context[self.context_var] = latest_posts
        return u""


@register.tag
def latest_blog_posts(parser, token):
    bits = token.split_contents()
    return LatestBlogPostsNode(bits[2])


class LatestBlogPostNode(template.Node):
    
    def __init__(self, context_var):
        self.context_var = context_var
    
    def render(self, context):
        try:
            latest_post = Post.objects.current()[0]
        except IndexError:
            latest_post = None
        context[self.context_var] = latest_post
        return u""


@register.tag
def latest_blog_post(parser, token):
    bits = token.split_contents()
    return LatestBlogPostNode(bits[2])


class LatestSectionPostNode(template.Node):
    
    def __init__(self, section, context_var):
        self.section = template.Variable(section)
        self.context_var = context_var
    
    def render(self, context):
        section = self.section.resolve(context)
        post = Post.objects.section(section, queryset=Post.objects.current())
        try:
            post = post[0]
        except IndexError:
            post = None
        context[self.context_var] = post
        return u""


@register.tag
def latest_section_post(parser, token):
    """
        {% latest_section_post "articles" as latest_article_post %}
    """
    bits = token.split_contents()
    return LatestSectionPostNode(bits[1], bits[3])


class BlogSectionsNode(template.Node):
    
    def __init__(self, context_var):
        self.context_var = context_var
    
    def render(self, context):
        sections = [(ALL_SECTION_NAME, "All")] + SECTIONS
        context[self.context_var] = sections
        return u""


@register.tag
def blog_sections(parser, token):
    """
        {% blog_sections as blog_sections %}
    """
    bits = token.split_contents()
    return BlogSectionsNode(bits[2])
