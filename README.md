![](http://pinaxproject.com/pinax-design/patches/pinax-blog.svg)

# Pinax Blog

[![](https://img.shields.io/pypi/v/pinax-blog.svg)](https://pypi.python.org/pypi/pinax-blog/)
[![](https://img.shields.io/badge/license-MIT-blue.svg)](https://pypi.python.org/pypi/pinax-blog/)

[![CircleCi](https://img.shields.io/circleci/project/github/pinax/pinax-blog.svg)](https://circleci.com/gh/pinax/pinax-blog)
[![Codecov](https://img.shields.io/codecov/c/github/pinax/pinax-blog.svg)](https://codecov.io/gh/pinax/pinax-blog)
![](https://img.shields.io/github/contributors/pinax/pinax-blog.svg)
![](https://img.shields.io/github/issues-pr/pinax/pinax-blog.svg)
![](https://img.shields.io/github/issues-pr-closed/pinax/pinax-blog.svg)

[![](http://slack.pinaxproject.com/badge.svg)](http://slack.pinaxproject.com/)


`pinax-blog` is a blog app for Django.

Current features include:

* support for multiple channels (e.g. technical vs business)
* use of Creole (optional) and Markdown as markup format
* Atom and RSS feeds
* previewing of blog posts before publishing
* optional ability to announce new posts on twitter
* Traditional date based urls or simpler slug-only urls, via configuration
* Control over opengraph and twitter card meta data per post
* Review comments per post for multi-author workflows
* public but secret urls for unpublished blog posts for easier review

### Supported Django and Python Versions

* Django 1.8, 1.10, 1.11, and 2.0
* Python 2.7, 3.4, 3.5, and 3.6


## Table of Contents

* [Installation](#installation)
* [Usage](#usage)
* [Customizing Admin](#customizing-admin)
* [Templates](#templates)
* [Dependencies](#dependencies)
* [Change Log](#change-log)
* [Project History](#project-history)
* [About Pinax](#about-pinax)


## Installation

To install pinax-blog:

    pip install pinax-blog

Add `pinax.blog` to your `INSTALLED_APPS` setting:

    INSTALLED_APPS = (
        ...
        "pinax.blog",
        ...
    )

Add `pinax.blog.urls` to your project urlpatterns:

    urlpatterns = [
        ...
        url(r"^blog/", include("pinax.blog.urls", namespace="pinax_blog")),
        ...
    ]

Optionally, if you want `creole` support for a mark up choice:

    pip install creole

NOTE: the `creole` package does not support Python 3


## Usage

You work with this app as an author via the Django Admin.

You can [customize](customize-admin.md) the editor for the admin at the site
level or just use the stock text areas.

The `description` field in the admin represents the text that will be used in
different HTML META header tags that are useful for controlling the display
on social networks like Twitter and Facebook.

This is the same idea behind the `primary_image` field in the admin.


### Images

There are custom `markdown` and `creole` extensions for embedding images that
have been uploaded via the inline on the post create or edit form in the admin.

You first upload the image or images you want to use in the post by selecting
them in the file selector in the images section, and then hitting "Save and
Continue Editing". Once the form reloads, you'll see indicators above each
uploaded image with a number between two brackets, e.g. `{{ 25 }}`.

This is the syntax if you are using `creole` for adding that image to your
post. You can just copy and paste that.

If you are using `markdown` however, you will need to use the following
markup in your post:

    ![Alt Text](25)

or without alt text:

    ![](25)

Adjusting for the number of the image, of course.


### Scoping

The idea of scoping allows you to setup your project to have multiple blogs
partitioned by whatever domain object you would like.

#### Settings

* `PINAX_BLOG_SCOPING_MODEL` - a string in the format `"app.Model"` that will set a ForeignKey on the `blog.Post` model
* `PINAX_BLOG_SCOPING_URL_VAR` - the url variable name that you use in your url prefix that will allow you to look up your scoping object
* `PINAX_BLOG_HOOKSET` - introducing the hookset pattern from other apps.  just a single method: `get_blog(self, **kwargs)` is defined.  override this in your project to the `Blog` object that will scope your posts.  By default there is only one `Blog` instance and that is returned.
* `pinax.blog.context_processors.scoped` - add to your context processors to put `scoper_lookup` in templates for url reversing

#### Example

To demonstrate how to set all this up let's walk through an example where we
will scope by `auth.User` so that each user has their own blog at `/users/:username/`.

First we will modify the `settings.py`:

```python
# ... abbreviated for clarity

TEMPLATES = [
    {
        # ...
        "OPTIONS": {
            # ...
            "context_processors": [
                # ...
                "pinax.blog.context_processors.scoped"
            ],
        },
    },
]

PINAX_BLOG_SCOPING_URL_VAR = "username"
PINAX_BLOG_SCOPING_MODEL = "auth.User"
PINAX_BLOG_HOOKSET = "multiblog.hooks.HookSet"  # where `multiblog` is the package name of our project
```

Now, we'll add the url in `urls.py`:

```python
url(r"^users/(?P<username>[-\w]+)/", include("pinax.blog.urls", namespace="pinax_blog"))
```

And finally we'll implement our hookset by adding a `hooks.py`:

```python
from django.contrib.auth.models import User


class HookSet(object):

    def get_blog(self, **kwargs):
        username = kwargs.get("username", None)
        return User.objects.get(username=username).blog
```

This is designed to work out of the box with templates in `pinax-theme-bootstrap`
so you can either use them directly or use them as a reference.  If you need to
reverse a URL for any of the `pinax-blog` urls you can simply do:

```django
{% url "pinax_blog:blog" scoper_lookup %}
```


## Customizing Admin

Customizing the admin functionality can be as complex as overriding the `ModelAdmin`
and `ModelForm` that ships with `pinax-blog` or as simple as just overriding
the `admin/blog/post/change_form.html` template.

Here is an example of an actual customization to use the [ACE Editor](http://ace.c9.io/) for
teaser and body content:

    {% extends "admin/change_form.html" %}
    {% load i18n admin_urls %}
    {% block extrahead %}
        {{ block.super }}
        <script src="//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
        <script src="//cdnjs.cloudflare.com/ajax/libs/ace/1.1.8/ace.js"></script>
        <script>
        $(function () {
            var contentDiv = $("<div>").attr("id", "content-editor"),
                teaserDiv = $("<div>").attr("id", "teaser-editor"),
                setupEditor = function (editor, textarea) {
                    editor.setTheme("ace/theme/twilight");
                    editor.getSession().setMode("ace/mode/markdown");
                    editor.getSession().setValue(textarea.val());
                    editor.getSession().setUseWrapMode(true);
                    editor.getSession().on('change', function(){
                      textarea.val(editor.getSession().getValue());
                    });
                    editor.getSession().setTabSize(4);
                    editor.getSession().setUseSoftTabs(true);
                };
            $(".field-content div").append(contentDiv);
            $(".field-teaser div").append(teaserDiv);
            var editor1 = ace.edit("content-editor");
            var editor2 = ace.edit("teaser-editor");
            var textarea1 = $('textarea[name="content"]').hide();
            var textarea2 = $('textarea[name="teaser"]').hide();
            setupEditor(editor1, textarea1);
            setupEditor(editor2, textarea2);
        });
        </script>
        <style type="text/css" media="screen">
        #content-editor {
            min-height: 300px;
            width: 80%;
            min-width: 800px;
        }
        #teaser-editor {
            min-height: 100px;
            width: 80%;
            min-width: 800px;
        }
    </style>
    {% endblock %}


## Templates

All templates for this app should be located in the subfolder of `pinax/blog/`
in your template search path.

## Blog List

The `BlogIndexView` and `SectionIndexView` both render the template
`pinax/blog/blog_list.html` with `post_list`, `search_query`, `current_section`
context variables, where `current_section` is either a `Section` object or the
string `"all"`.

The `post_list` variable is a queryset of current blog posts. If the `GET` parameter,
`q` is found, it filters the queryset create a simple search mechanism, then
assigns the value to `search_query`.


## Post Detail

The four blog detail views (`DateBasedPostDetailView`, `SecretKeyPostDetailView`,
`SlugUniquePostDetailView`, and `StaffPostDetailView`) all render the template
`pinax/blog/blog_post.html` with the `post` and `current_section` context
variables.

The `post` is the requested post. It may or may not be public depending on the
url requested.


## Blog Feeds

The url `blog_feed` will either render `pinax/blog/atom_feed.xml` or
`pinax/blog/rss_feed.xml` depending on the parameters in the URL. It will pass
both templates the context variables of `feed_id`, `feed_title`, `blog_url`,
`feed_url`, `feed_updated`, `entries`, and `current_site`.

Both templates ship already configured to work out of the box.


## Dependencies

* django-appconf
* pytz
* pillow
* markdown
* pygments
* pinax-images

See `setup.py` for specific required versions of these packages.


## Change Log

### 6.1.0

* Add Django 2.0 compatibility testing
* Drop Django 1.9 and Python 3.3 support
* Move documentation into README
* Convert CI and coverage to CircleCi and CodeCov
* Add PyPi-compatible long description

### 6.0.3

* `scoped` context processor handles case when `request.resolver_match` is None

### 6.0.2

* increased max_length of Post.slug field from 50 to 90 chars, matching Post.title field length.

### 6.0.1

* fix templatetag scoping

### 6.0.0

* added support for frontend editing
* removed twitter integrations
* swapped out internal image management for pinax-images
* added a `Blog` scoping model and enabled site defined one to one relationship
  custom site-defined scoping.

### 5.0.2

* updated pytz version ([PR #92](https://github.com/pinax/pinax-blog/pull/92))
* updated docs ([PR #87](https://github.com/pinax/pinax-blog/pull/87), [PR #89](https://github.com/pinax/pinax-blog/pull/89))

### 5.0.1

* Fixed feed_url creation in blog_feed view ([PR #82](https://github.com/pinax/pinax-blog/pull/82))
* Updated docs to use url namespace ([PR #87](https://github.com/pinax/pinax-blog/pull/87))

### 5.0.0

* Initial version for core distribution

## Project History

This app used to be named `biblion` when originally developed by Eldarion, Inc.
After donation to Pinax, the app was renamed to `pinax-blog`, making it easier
to find and know what it is.


## About Pinax

Pinax is an open-source platform built on the Django Web Framework. It is an ecosystem of reusable Django apps, themes, and starter project templates. This collection can be found at http://pinaxproject.com.

The Pinax documentation is available at http://pinaxproject.com/pinax/. If you would like to help us improve our documentation or write more documentation, please join our Pinax Project Slack team and let us know!

For updates and news regarding the Pinax Project, please follow us on Twitter at @pinaxproject and check out our blog http://blog.pinaxproject.com.
