# pinax-blog

Originally named `biblion`, the eldarion.com blog app intended to be suitable
for site-level company and project blogs, is now known as `pinax-blog`.

!!! note "Pinax Ecosystem"
    This app was developed as part of the Pinax ecosystem but is just a Django app
    and can be used independently of other Pinax apps.

    To learn more about Pinax, see <http://pinaxproject.com/>


## Quickstart

Install the development version:

    pip install pinax-blog

Add `pinax-blog` to your `INSTALLED_APPS` setting.
Add dependency `pinax-images` to your `INSTALLED_APPS` setting as well.
Also add the `sites` framework if you don't already use it:

    INSTALLED_APPS = (
        # ...
        "django.contrib.sites"
        "pinax.blog",
        "pinax.images",
        # ...
    )

    SITE_ID = 1

Run the migration `python manage.py migrate`

Add entry to your `urls.py`:

    urlpatterns = [
        # ...
        url(r"^blog/", include("pinax.blog.urls", namespace="pinax_blog")),
        url(r"^ajax/images/", include("pinax.images.urls", namespace="pinax_images")),
        # ...
    ]


## Dependencies

* `django-appconf>=1.0.1`
* `pytz>=2016.6.1`
* `Pillow>=3.0.0`
* `Markdown>=2.6.5`
* `Pygments>=2.0.2`
* `pinax-images>=2.0.0`

Optionally, if you want `creole` support for a mark up choice:

    pip install creole

NOTE: the `creole` package does not support Python 3
