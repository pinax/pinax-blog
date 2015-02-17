from __future__ import unicode_literals

import pkg_resources


extensions = []
templates_path = []
source_suffix = ".rst"
master_doc = "index"
project = "pinax-blog"
copyright_holder = "Eldarion, Inc."
copyright = "2015, {0}".format(copyright_holder)
exclude_patterns = ["_build"]
pygments_style = "sphinx"
html_theme = "default"
htmlhelp_basename = "{0}doc".format(project)
latex_documents = [(
    "index",
    "{0}.tex".format(project),
    "{0} Documentation".format(project),
    "Pinax",
    "manual"
),]
man_pages = [(
    "index",
    project,
    "{0} Documentation".format(project),
    ["Pinax"],
    1
),]

version = pkg_resources.get_distribution("pinax-blog").version
release = version
