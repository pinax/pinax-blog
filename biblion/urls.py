from django.conf.urls.defaults import patterns, url

import biblion.views


urlpatterns = patterns("",
    url(r"^$", biblion.views.BiblionList.as_view(), name="biblion_list"),
    url(r"^create/$", biblion.views.BiblionCreate.as_view(), name="biblion_create"),
    url(r"^blog/(?P<slug>[\w-])/$", biblion.views.BiblionDetail.as_view(), name="biblion_detail"),
)
