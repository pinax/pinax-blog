from django.conf.urls.defaults import patterns, url

from biblion.views import BiblionList


urlpatterns = patterns("",
    url(r"^$", BiblionList.as_view(), name="biblion_list"),
)
