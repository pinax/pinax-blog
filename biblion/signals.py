import django.dispatch


post_viewed = django.dispatch.Signal(providing_args=["post","request"])
