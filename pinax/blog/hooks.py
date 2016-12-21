from pinax.blog.conf import settings


class PinaxBlogDefaultHookSet(object):

    def get_scoped_object(self, **kwargs):
        return None


class HookProxy(object):

    def __getattr__(self, attr):
        return getattr(settings.PINAX_BLOG_HOOKSET, attr)


hookset = HookProxy()
