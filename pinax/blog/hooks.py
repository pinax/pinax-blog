from django.http import Http404

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

    def get_url_var(self, scoper):
        return None

    def get_blog_str(self, blog):
        return "Blog {}".format(blog.pk)

    def can_manage(self, request, *args, **kwargs):
        return request.user.is_staff

    def response_cannot_manage(self, request, *args, **kwargs):
        """
        The response to return when `can_manage` returns `False` for all of the
        manage views.  You may want to return a `redirect` or raise some HTTP
        error.
        """
        raise Http404()


class HookProxy(object):

    def __getattr__(self, attr):
        return getattr(settings.PINAX_BLOG_HOOKSET, attr)


hookset = HookProxy()
