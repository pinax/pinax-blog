from distutils.core import setup, find_packages

# see requirements.txt for dependencies



setup(
    name = "biblion",
    version = "0.2.dev3",
    author = "Eldarion",
    author_email = "development@eldarion.com",
    description = "the eldarion.com blog app intended to be suitable for site-level company and project blogs",
    long_description = open("README.rst").read(),
    license = "BSD",
    url = "http://github.com/eldarion/biblion",
    packages=find_packages(),
    install_requires=[
        "creole==1.2",
        "docutils==0.8.1",
        "Markdown==2.0.3",
        "Pygments==1.4",
        "textile==2.1.5",
    ],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ],
    # Make setuptools include all data files under version control,
    # svn and CVS by default
    include_package_data=True,
    # Tells setuptools to download setuptools_git before running setup.py so
    # it can find the data files under Git version control.
    setup_requires=["setuptools_git"],
    zip_safe=False,
)
