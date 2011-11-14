from django import template

from biblion.models import Post, Section


register = template.Library()


class LatestBiblionPostsNode(template.Node):
    
    def __init__(self, biblion, context_var):
        self.biblion = template.Variable(biblion)
        self.context_var = context_var
    
    def render(self, context):
        biblion = self.biblion.resolve(context)
        latest_posts = biblion.posts.current()[:5]
        context[self.context_var] = latest_posts
        return u""


@register.tag
def latest_biblion_posts(parser, token):
    """
        {% latest_biblion_posts biblion as posts %}
    """
    bits = token.split_contents()
    return LatestBiblionPostsNode(bits[1], bits[3])


class LatestBiblionPostNode(template.Node):
    
    def __init__(self, biblion, context_var):
        self.biblion = template.Variable(biblion)
        self.context_var = context_var
    
    def render(self, context):
        biblion = self.biblion.resolve(context)
        try:
            latest_post = biblion.posts.current()[0]
        except IndexError:
            latest_post = None
        context[self.context_var] = latest_post
        return u""


@register.tag
def latest_biblion_post(parser, token):
    bits = token.split_contents()
    return LatestBiblionPostNode(bits[1], bits[2])
