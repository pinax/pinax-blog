import django.dispatch

post_viewed = django.dispatch.Signal()
post_published = django.dispatch.Signal()
post_redirected = django.dispatch.Signal()
