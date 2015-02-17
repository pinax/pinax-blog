from django.conf.urls import url, patterns


urlpatterns = patterns(
    "pinax.blog.views",
    url(r'^$', "blog_index", name="blog"),
    url(r'^section/(?P<section>[-\w]+)/$', "blog_section_list", name="blog_section"),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$', "blog_post_detail", name="blog_post"),
    url(r'^(?P<post_slug>[-\w]+)/$', "blog_post_detail", name="blog_post_slug"),
    url(r'^post/(?P<post_pk>\d+)/$', "blog_post_detail", name="blog_post_pk"),
    url(r'^post/(?P<post_secret_key>\w+)/$', "blog_post_detail", name="blog_post_secret"),
    url(r'^feed/(?P<section>[-\w]+)/(?P<feed_type>[-\w]+)/$', "blog_feed", name="blog_feed"),
)
