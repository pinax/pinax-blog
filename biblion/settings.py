from django.conf import settings



ALL_SECTION_NAME = getattr(settings, "BIBLION_ALL_SECTION_NAME", "all")
SECTIONS = getattr(settings, "BIBLION_SECTIONS", [])
