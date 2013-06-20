from django.conf.urls import patterns, url


urlpatterns = patterns("",
    url(r'^$', "biblion.views.blog_index", name="blog"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$', "biblion.views.blog_post_detail", name="blog_post"),
    url(r'^post/(?P<post_pk>\d+)/$', "biblion.views.blog_post_detail", name="blog_post_pk"),
    url(r'^(?P<section>[-\w]+)/$', "biblion.views.blog_section_list", name="blog_section"),
)