import django.dispatch


post_created = django.dispatch.Signal(providing_args=["post", "request"])
post_updated = django.dispatch.Signal(providing_args=["post", "request"])
post_deleted = django.dispatch.Signal(providing_args=["post", "request"])
