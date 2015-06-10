from django.core.exceptions import ImproperlyConfigured
try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

try:
    import twitter
except ImportError:
    twitter = None


from .conf import settings


def can_tweet():
    creds_available = (hasattr(settings, "TWITTER_USERNAME") and
                       hasattr(settings, "TWITTER_PASSWORD"))
    return twitter and creds_available


def load_path_attr(path):
    i = path.rfind(".")
    module, attr = path[:i], path[i + 1:]
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured("Error importing %s: '%s'" % (module, e))
    try:
        attr = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured("Module '%s' does not define a '%s'" % (module, attr))
    return attr
