try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse  # noqa
