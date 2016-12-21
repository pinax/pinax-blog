from .conf import settings


def scoped(request):
    return {
        "scoped_var": request.resolver_match.kwargs.get(settings.PINAX_BLOG_SCOPING_URL_VAR)
    }
