from django.conf import settings


PARSER = getattr(settings, "BIBLION_PARSER", ["biblion.creole_parser.parse", {}])
ALL_SECTION_NAME = getattr(settings, "BIBLION_ALL_SECTION_NAME", "all")
SECTIONS = getattr(settings, "BIBLION_SECTIONS", [])