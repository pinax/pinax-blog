from django import template

from biblion.models import Post


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
