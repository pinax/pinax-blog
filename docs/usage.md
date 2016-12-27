# Usage

You work with this app as an author via the Django Admin.

You can [customize](customize-admin.md) the editor for the admin at the site
level or just use the stock text areas.

The `description` field in the admin represents the text that will be used in
different HTML META header tags that are useful for controlling the display
on social networks like Twitter and Facebook.

This is the same idea behind the `primary_image` field in the admin.


## Images

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


## Scoping

The idea of scoping allows you to setup your project to have multiple blogs
partitioned by whatever domain object you would like.

### Settings

* `PINAX_BLOG_SCOPING_MODEL` - a string in the format `"app.Model"` that will set a ForeignKey on the `blog.Post` model
* `PINAX_BLOG_SCOPING_URL_VAR` - the url variable name that you use in your url prefix that will allow you to look up your scoping object
* `PINAX_BLOG_HOOKSET` - introducing the hookset pattern from other apps.  just a single method: `get_blog(self, **kwargs)` is defined.  override this in your project to the `Blog` object that will scope your posts.  By default there is only one `Blog` instance and that is returned.
* `pinax.blog.context_processors.scoped` - add to your context processors to put `scoper_lookup` in templates for url reversing

### Example

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

Now that you have the context processor installed.
