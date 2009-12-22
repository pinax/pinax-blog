from distutils.core import setup


setup(
    name = "biblion",
    version = "0.1.0-dev1",
    author = "Eldarion",
    author_email = "development@eldarion.com",
    description = "contact importing for Django",
    long_description = open("README.rst").read(),
    license = "BSD",
    url = "http://github.com/eldarion/biblion",
    packages = [
        "biblion",
        "biblion.templatetags",
    ],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ]
)