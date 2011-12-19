from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template.defaultfilters import slugify
try:
    from django.utils.importlib import import_module
except ImportError:
    from importlib import import_module

try:
    import twitter
except ImportError:
    twitter = None


def can_tweet():
    creds_available = (
        hasattr(settings, "TWITTER_USERNAME") and hasattr(settings, "TWITTER_PASSWORD")
    )
    return twitter and creds_available


def slugify_unique(value, model, slugfield="slug"):
        suffix = 0
        potential = base = slugify(value)
        while True:
            if suffix:
                potential = "-".join([base, str(suffix)])
            if not model.objects.filter(**{slugfield: potential}).count():
                print model.objects.filter(**{slugfield: potential})
                return potential
            suffix += 1


def load_path_attr(path):
    i = path.rfind(".")
    module, attr = path[:i], path[i+1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured("Error importing %s: '%s'" % (module, e))
    try:
        attr = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured("Module '%s' does not define a '%s'" % (module, attr))
    return attr
