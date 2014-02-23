import codecs

from os import path
from setuptools import find_packages, setup


def read(*parts):
    filename = path.join(path.dirname(__file__), *parts)
    with codecs.open(filename, encoding="utf-8") as fp:
        return fp.read()


PACKAGE = "biblion"
NAME = "biblion"
DESCRIPTION = "the eldarion.com blog app intended to be suitable for site-level company and project blogs"
AUTHOR = "Eldarion"
AUTHOR_EMAIL = "paltman@eldarion.com"
URL = "http://github.com/eldarion/biblion"
VERSION = __import__(PACKAGE).__version__


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=read("README.rst"),
    url=URL,
    license="BSD",
    packages=find_packages(),
    package_data = {
        "biblion": [
            "templates/biblion/*.xml",
        ]
    },
    install_requires=[
        "django-appconf>=0.5",
        "Pillow>=2.0",
        "creole>=1.2",
        "Markdown>=2.4",
        "Pygments>=1.6"
    ],
    tests_require=[
        "Django>=1.4",
    ],
    test_suite="runtests.runtests",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False
)
