from __future__ import unicode_literals

from django.conf import settings  # noqa

from appconf import AppConf


def is_installed(package):
    try:
        __import__(package)
        return True
    except ImportError:
        return False


DEFAULT_MARKUP_CHOICE_MAP = {
    "markdown": {"label": "Markdown", "parser": "pinax.blog.parsers.markdown_parser.parse"}
}
if is_installed("creole"):
    DEFAULT_MARKUP_CHOICE_MAP.update({
        "creole": {"label": "Creole", "parser": "pinax.blog.parsers.creole_parser.parse"},
    })


class PinaxBlogAppConf(AppConf):

    ALL_SECTION_NAME = "all"
    SECTIONS = []
    UNPUBLISHED_STATES = [
        "Draft"
    ]
    FEED_TITLE = "Blog"
    SECTION_FEED_TITLE = "Blog (%s)"
    MARKUP_CHOICE_MAP = DEFAULT_MARKUP_CHOICE_MAP
    MARKUP_CHOICES = DEFAULT_MARKUP_CHOICE_MAP
    SLUG_UNIQUE = False

    def configure_markup_choices(self, value):
        return [
            (key, value[key]["label"])
            for key in value.keys()
        ]

    class Meta:
        prefix = "pinax_blog"
