from django.conf.urls import include


urlpatterns = [
    (r"^", include("pinax.blog.urls")),
]
