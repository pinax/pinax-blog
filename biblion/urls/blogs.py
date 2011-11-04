from django.conf.urls.defaults import *

from biblion.views import BlogList, BlogCreate


urlpatterns = patterns("",
    url(r"^$", BlogList.as_view(), name="blog_list"),
    url(r"^create/$", BlogCreate.as_view(), name="blog_create"),
    url(r"^(?P<blog_slug>[-\w]+)/", include("biblion.urls.posts")),
)