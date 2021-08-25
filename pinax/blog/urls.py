from django.conf.urls import re_path

from .conf import settings
from .views import (
    BlogIndexView,
    DateBasedPostDetailView,
    ManageCreatePost,
    ManageDeletePost,
    ManagePostList,
    ManageUpdatePost,
    SecretKeyPostDetailView,
    SectionIndexView,
    SlugUniquePostDetailView,
    StaffPostDetailView,
    ajax_preview,
    blog_feed,
)

app_name = "pinax_blog"

urlpatterns = [
    re_path(r"^$", BlogIndexView.as_view(), name="blog"),
    re_path(r"^section/(?P<section>[-\w]+)/$", SectionIndexView.as_view(), name="blog_section"),
    re_path(r"^post/(?P<post_pk>\d+)/$", StaffPostDetailView.as_view(), name="blog_post_pk"),
    re_path(r"^post/(?P<post_secret_key>\w+)/$", SecretKeyPostDetailView.as_view(), name="blog_post_secret"),
    re_path(r"^feed/(?P<section>[-\w]+)/(?P<feed_type>[-\w]+)/$", blog_feed, name="blog_feed"),

    # authoring
    re_path(r"^manage/posts/$", ManagePostList.as_view(), name="manage_post_list"),
    re_path(r"^manage/posts/create/$", ManageCreatePost.as_view(), name="manage_post_create"),
    re_path(r"^manage/posts/(?P<post_pk>\d+)/update/$", ManageUpdatePost.as_view(), name="manage_post_update"),
    re_path(r"^manage/posts/(?P<post_pk>\d+)/delete/$", ManageDeletePost.as_view(), name="manage_post_delete"),

    re_path(r"^ajax/markdown/preview/$", ajax_preview, name="ajax_preview")
]


if settings.PINAX_BLOG_SLUG_UNIQUE:
    urlpatterns += [
        re_path(r"^(?P<post_slug>[-\w]+)/$",
            SlugUniquePostDetailView.as_view(),
            name="blog_post_slug")
    ]
else:
    urlpatterns += [
        re_path(r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$",
            DateBasedPostDetailView.as_view(),
            name="blog_post"),
    ]
