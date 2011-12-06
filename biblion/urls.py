from django.conf.urls.defaults import patterns, url

import biblion.views


urlpatterns = patterns("",
    url(r"^$", biblion.views.BiblionList.as_view(), name="biblion_list"),
    url(r"^create/$", biblion.views.BiblionCreate.as_view(), name="biblion_create"),
    url(r"^blog/(?P<slug>[\w-]+)/$", biblion.views.BiblionDetail.as_view(), name="biblion_detail"),
    url(r"^blog/(?P<slug>[\w-]+)/update/$", biblion.views.BiblionUpdate.as_view(), name="biblion_update"),
    url(r"^blog/(?P<slug>[\w-]+)/post/$", biblion.views.PostCreate.as_view(), name="biblion_post_create"),
    url(r"^post/(?P<slug>[\w-]+)/$", biblion.views.PostDetail.as_view(), name="biblion_post_detail"),
    url(r"^post/(?P<slug>[\w-]+)/edit/$", biblion.views.PostUpdate.as_view(), name="biblion_post_edit"),
)
