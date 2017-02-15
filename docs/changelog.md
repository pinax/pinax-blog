# Change Log

## 6.0.3

* `scoped` context processor handles case when `request.resolver_match` is None

## 6.0.2

* increased max_length of Post.slug field from 50 to 90 chars, matching Post.title field length.

## 6.0.1

* fix templatetag scoping

## 6.0.0

* added support for frontend editing
* removed twitter integrations
* swapped out internal image management for pinax-images
* added a `Blog` scoping model and enabled site defined one to one relationship
  custom site-defined scoping.

## 5.0.2

* updated pytz version ([PR #92](https://github.com/pinax/pinax-blog/pull/92))
* updated docs ([PR #87](https://github.com/pinax/pinax-blog/pull/87), [PR #89](https://github.com/pinax/pinax-blog/pull/89))

## 5.0.1

* Fixed feed_url creation in blog_feed view ([PR #82](https://github.com/pinax/pinax-blog/pull/82))
* Updated docs to use url namespace ([PR #87](https://github.com/pinax/pinax-blog/pull/87))

## 5.0.0

* Initial version for core distribution
