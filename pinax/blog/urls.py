from django.conf.urls import url

from .conf import settings
from .views import (
    BlogIndexView,
    DateBasedPostDetailView,
    SecretKeyPostDetailView,
    SectionIndexView,
    SlugUniquePostDetailView,
    StaffPostDetailView,
    blog_feed,
    ManagePostList,
    ManageCreatePost,
    ManageUpdatePost,
    ManageDeletePost,
    ajax_preview
)


urlpatterns = [
    url(r"^$", BlogIndexView.as_view(), name="blog"),
    url(r"^section/(?P<section>[-\w]+)/$", SectionIndexView.as_view(), name="blog_section"),
    url(r"^post/(?P<post_pk>\d+)/$", StaffPostDetailView.as_view(), name="blog_post_pk"),
    url(r"^post/(?P<post_secret_key>\w+)/$", SecretKeyPostDetailView.as_view(), name="blog_post_secret"),
    url(r"^feed/(?P<section>[-\w]+)/(?P<feed_type>[-\w]+)/$", blog_feed, name="blog_feed"),

    # authoring
    url(r"^manage/posts/$", ManagePostList.as_view(), name="manage_post_list"),
    url(r"^manage/posts/create/$", ManageCreatePost.as_view(), name="manage_post_create"),
    url(r"^manage/posts/(?P<post_pk>\d+)/update/$", ManageUpdatePost.as_view(), name="manage_post_update"),
    url(r"^manage/posts/(?P<post_pk>\d+)/delete/$", ManageDeletePost.as_view(), name="manage_post_delete"),

    url(r"^ajax/markdown/preview/$", ajax_preview, name="ajax_preview")
]


if settings.PINAX_BLOG_SLUG_UNIQUE:
    urlpatterns += [
        url(r"^(?P<post_slug>[-\w]+)/$",
            SlugUniquePostDetailView.as_view(),
            name="blog_post_slug")
    ]
else:
    urlpatterns += [
        url(r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$",
            DateBasedPostDetailView.as_view(),
            name="blog_post"),
    ]
