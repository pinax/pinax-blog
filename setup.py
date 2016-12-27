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
    version="6.0.0",
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
    tests_require=[
        "pinax-theme-bootstrap>=7.4.0",
    ],
    install_requires=[
        "django-appconf>=1.0.1",
        "pytz>=2016.6.1",
        "Pillow>=3.0.0",
        "Markdown>=2.6.5",
        "Pygments>=2.0.2",
        "pinax-images>=2.0.0"
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
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False
)
