import codecs

from os import path
from setuptools import find_packages, setup


def read(*parts):
    filename = path.join(path.dirname(__file__), *parts)
    with codecs.open(filename, encoding="utf-8") as fp:
        return fp.read()

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, "rst").replace("\r","")
except (ImportError, IOError):
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: read(f)

setup(
    author="Pinax Team",
    author_email="team@pinaxprojects.com",
    description="Blogging app for the Django web framework",
    name="pinax-blog",
    long_description=read_md("README.md"),
    version="6.1",
    url="http://github.com/pinax/pinax-blog/",
    license="MIT",
    packages=find_packages(),
    package_data={
        "pinax.blog": [
            "templates/pinax/blog/*.xml",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "django>=1.8",
        "django-appconf>=1.0.1",
        "pytz>=2016.6.1",
        "Pillow>=3.0.0",
        "Markdown>=2.6.5",
        "Pygments>=2.0.2",
        "pinax-images>=2.0.0",
    ],
    tests_require=[
        "pinax-theme-bootstrap>=7.4.0",
    ],
    test_suite="runtests.runtests",
    zip_safe=False
)
