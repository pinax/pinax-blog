==============
Biblion README
==============

Biblion was the eldarion.com blog which we've extracted and open sourced. It
is currently positioned as being used for site/project blogs such as
eldarion.com and pinaxproject.com. We intend for this app to replace the
internal Pinax blog app once we've made it feature complete.


Current features include:

* support for multiple channels (e.g. technical vs business)
* use of Creole as markup format
* Atom feeds
* previewing of blog posts before publishing
* optional ability to announce new posts on twitter


Setup Biblion in your project:

1. add to your ``INSTALLED_APPS``: ``'biblion',``
2. add to your ``urlpatterns`` something like: ``url(r'^blog/', include('biblion.urls')),``
3. run ``$ python manage.py syncdb``
4. run ``$ python manage.py runserver``
5. go to http://127.0.0.1:8000/admin/ and add some posts in the "biblion" section
6. go to http://127.0.0.1:8000/blog/ and enjoy!

