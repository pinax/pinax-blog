import codecs

from os import path
from setuptools import find_packages, setup


def read(*parts):
    filename = path.join(path.dirname(__file__), *parts)
    with codecs.open(filename, encoding="utf-8") as fp:
        return fp.read()


NAME = "pinax-blog"
DESCRIPTION = "a Django blog app"
AUTHOR = "Pinax Team"
AUTHOR_EMAIL = "team@pinaxproject.com"
URL = "https://github.com/pinax/pinax-blog"


setup(
    name=NAME,
    version="3.1.2",
    description=DESCRIPTION,
    long_description=read("README.rst"),
    url=URL,
    license="MIT",
    packages=find_packages(),
    package_data={
        "pinax.blog": [
            "templates/pinax/blog/*.xml",
        ]
    },
    install_requires=[
        "django-appconf>=1.0.1",
        "Pillow>=2.0",
        "creole>=1.2",
        "Markdown>=2.4",
        "Pygments>=1.6"
    ],
    test_suite="runtests.runtests",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False
)
