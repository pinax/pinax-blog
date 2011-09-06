from django.conf import settings


PARSER = getattr(settings, "BIBLION_PARSER", ["biblion.creole_parser.parse", {}])
