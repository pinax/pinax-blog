# Templates

All the templates for this app should be located in the subfolder of `pinax/blog/`
in your template search path.

## Blog List

The url `blog` and `blog_section` both render the template
`pinax/blog/blog_list.html` with `posts`, `search_query`, `section_slug`,
and `section_name` context variables.

The `posts` variable is a queryset of current blog posts. If the `GET` parameter,
`q` is found, it filters the queryset create a simple search mechanism, then
assigns the value to `search_query`. If the `blog` url is requested then
`section` and `section_name` will be `None`.


## Post Detail

The urls, `blog_post`, `blog_post_pk`, `blog_post_slug`, and `blog_post_secret`
all render the template `pinax/blog/blog_post.html` with the `post` context
variable.

The `post` is the requested post. It may or may not be public depending on the
url requested.


## Blog Feeds

The url `blog_feed` will either render `pinax/blog/atom_feed.xml` or
`pinax/blog/rss_feed.xml` depending on the parameters in the URL. It will pass
both templates the context variables of `feed_id`, `feed_title`, `blog_url`,
`feed_url`, `feed_updated`, `entries`, and `current_site`.

Both of these templates ship already configured to work out of the box.


