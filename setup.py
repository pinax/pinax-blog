from setuptools import find_packages, setup

VERSION = "8.1.0"
LONG_DESCRIPTION = """
.. image:: http://pinaxproject.com/pinax-design/patches/pinax-blog.svg
    :target: https://pypi.python.org/pypi/pinax-blog/

==========
Pinax Blog
==========

.. image:: https://img.shields.io/pypi/v/pinax-blog.svg
    :target: https://pypi.python.org/pypi/pinax-blog/

\

.. image:: https://img.shields.io/circleci/project/github/pinax/pinax-blog.svg
    :target: https://circleci.com/gh/pinax/pinax-blog
.. image:: https://img.shields.io/codecov/c/github/pinax/pinax-blog.svg
    :target: https://codecov.io/gh/pinax/pinax-blog
.. image:: https://img.shields.io/github/contributors/pinax/pinax-blog.svg
    :target: https://github.com/pinax/pinax-blog/graphs/contributors
.. image:: https://img.shields.io/github/issues-pr/pinax/pinax-blog.svg
    :target: https://github.com/pinax/pinax-blog/pulls
.. image:: https://img.shields.io/github/issues-pr-closed/pinax/pinax-blog.svg
    :target: https://github.com/pinax/pinax-blog/pulls?q=is%3Apr+is%3Aclosed

\

.. image:: http://slack.pinaxproject.com/badge.svg
    :target: http://slack.pinaxproject.com/
.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://opensource.org/licenses/MIT/

\

``pinax-blog`` is a blog app for Django.

Features
--------

* support for multiple channels (e.g. technical vs business)
* use of Creole (optional) and Markdown as markup format
* Atom and RSS feeds
* previewing of blog posts before publishing
* optional ability to announce new posts on twitter
* Traditional date based urls or simpler slug-only urls, via configuration
* Control over opengraph and twitter card meta data per post
* Review comments per post for multi-author workflows
* public but secret urls for unpublished blog posts for easier review

Supported Django and Python Versions
------------------------------------

+-----------------+-----+-----+-----+
| Django / Python | 3.6 | 3.7 | 3.8 |
+=================+=====+=====+=====+
|  2.2            |  *  |  *  |  *  |
+-----------------+-----+-----+-----+
|  3.0            |  *  |  *  |  *  |
+-----------------+-----+-----+-----+
"""

setup(
    author="Pinax Team",
    author_email="team@pinaxproject.com",
    description="Blogging app for the Django web framework",
    name="pinax-blog",
    long_description=LONG_DESCRIPTION,
    version=VERSION,
    url="http://github.com/pinax/pinax-blog/",
    license="MIT",
    packages=find_packages(),
    package_data={
        "pinax.blog": [
            "templates/pinax/blog/*ml",
            "static/js/admin_post_form.js"
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "django>=2.2",
        "django-appconf>=1.0.1",
        "markdown==3.1.1",
        "pillow>=3.0.0",
        "pinax-images>=3.0.1",
        "pygments>=2.0.2",
        "pytz>=2020.1",
    ],
    tests_require=[
        "django-bootstrap-form>=3.0.0",
        "django-test-plus>=1.0.22",
        "mock>=2.0.0",
        "pinax-templates>=1.0.0",
    ],
    test_suite="runtests.runtests",
    zip_safe=False
)
