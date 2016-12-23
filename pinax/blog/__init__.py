import pkg_resources


__version__ = pkg_resources.get_distribution("pinax-blog").version
default_app_config = "pinax.blog.apps.AppConfig"
