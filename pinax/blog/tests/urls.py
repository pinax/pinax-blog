from django.conf.urls import include, url


urlpatterns = [
    url(r"^", include("pinax.blog.urls", namespace="pinax_blog")),
]
