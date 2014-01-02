from django.conf import settings


ALL_SECTION_NAME = getattr(settings, "BIBLION_ALL_SECTION_NAME", "all")
SECTIONS = getattr(settings, "BIBLION_SECTIONS", [])

DEFAULT_MARKUP_CHOICE_MAP = {
    "creole": {"label": "Creole", "parser": "biblion.parsers.creole_parser.parse"},
    "markdown": {"label": "Markdown", "parser": "biblion.parsers.markdown_parser.parse"}
}
MARKUP_CHOICE_MAP = getattr(settings, "BIBLION_MARKUP_CHOICE_MAP", DEFAULT_MARKUP_CHOICE_MAP)
MARKUP_CHOICES = [
    (key, MARKUP_CHOICE_MAP[key]["label"])
    for key in MARKUP_CHOICE_MAP.keys()
]
