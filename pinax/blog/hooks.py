from pinax.blog.conf import settings


class PinaxBlogDefaultHookSet(object):

    def get_blog(self, **kwargs):
        """
        By default there is a single Blog.

        In the event that there are multiple and/or those blogs are scoped by
        an external model, override this method to return the right blog given
        the `kwargs`.  These `kwargs` are the kwargs that come from the URL
        definition for the view.
        """
        from .models import Blog
        return Blog.objects.first()  # By default there is only a single blog

    def get_blog_str(self, blog):
        return "Blog {}".format(blog.pk)


class HookProxy(object):

    def __getattr__(self, attr):
        return getattr(settings.PINAX_BLOG_HOOKSET, attr)


hookset = HookProxy()
