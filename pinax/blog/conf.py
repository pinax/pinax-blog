from __future__ import unicode_literals

from django.conf import settings  # noqa

from appconf import AppConf


DEFAULT_MARKUP_CHOICE_MAP = {
    "creole": {"label": "Creole", "parser": "pinax.blog.parsers.creole_parser.parse"},
    "markdown": {"label": "Markdown", "parser": "pinax.blog.parsers.markdown_parser.parse"}
}


class PinaxBlogAppConf(AppConf):

    ALL_SECTION_NAME = "all"
    SECTIONS = []
    UNPUBLISHED_STATES = [
        "Draft"
    ]
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
