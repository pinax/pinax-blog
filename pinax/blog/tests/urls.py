from django.conf.urls import include, url

urlpatterns = [
    url(r"^", include("pinax.blog.urls", namespace="pinax_blog")),
    url(r"^ajax/images/", include("pinax.images.urls", namespace="pinax_images")),
]
