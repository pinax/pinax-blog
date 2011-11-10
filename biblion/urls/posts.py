from django.conf.urls.defaults import *


urlpatterns = patterns("",
    url(r"^$", "biblion.views.blog_index", name="blog"),
    url(r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$", "biblion.views.blog_post_detail", name="blog_post"),
    url(r"^post/(?P<post_pk>\d+)/$", "biblion.views.blog_post_detail", name="blog_post_pk"),
    url(r"^(?P<slug>[-\w]+)/$", "biblion.views.blog_section_list", name="blog_section"),
    url(r"post/add/$", "biblion.views.blog_post_add", name="blog_post_add"),
    url(r"^post/(?P<post_pk>\d+)/edit/$", "biblion.views.blog_post_edit", name="blog_post_edit"),
    url(r"^post/(?P<post_pk>\d+)/delete/$", "biblion.views.blog_post_delete", name="blog_post_delete"),
)