import django.dispatch


post_viewed = django.dispatch.Signal(providing_args=["post", "request"])
post_published = django.dispatch.Signal(providing_args=["post"])
post_redirected = django.dispatch.Signal(providing_args=["post", "request"])
