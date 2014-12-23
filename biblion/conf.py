from __future__ import unicode_literals

from django.conf import settings  # noqa

from appconf import AppConf


DEFAULT_MARKUP_CHOICE_MAP = {
    "creole": {"label": "Creole", "parser": "biblion.parsers.creole_parser.parse"},
    "markdown": {"label": "Markdown", "parser": "biblion.parsers.markdown_parser.parse"}
}


class BiblionAppConf(AppConf):

    ALL_SECTION_NAME = "all"
    SECTIONS = []
    MARKUP_CHOICE_MAP = DEFAULT_MARKUP_CHOICE_MAP
    MARKUP_CHOICES = DEFAULT_MARKUP_CHOICE_MAP
    SLUG_UNIQUE = False

    def configure_markup_choices(self, value):
        return [
            (key, value[key]["label"])
            for key in value.keys()
        ]
