from django.db import models
from django.db.models.query import Q

from .conf import settings
from .exceptions import InvalidSection


PUBLISHED_STATE = len(settings.PINAX_BLOG_UNPUBLISHED_STATES) + 1


class PostManager(models.Manager):

    def published(self):
        return self.filter(published__isnull=False, state=PUBLISHED_STATE)

    def current(self):
        return self.published().order_by("-published")

    def section(self, value, queryset=None):

        if queryset is None:
            queryset = self.published()

        if not value:
            return queryset
        else:
            try:
                section_idx = self.model.section_idx(value)
            except KeyError:
                raise InvalidSection
            all_sections = Q(section=self.model.section_idx(settings.PINAX_BLOG_ALL_SECTION_NAME))
            return queryset.filter(all_sections | Q(section=section_idx))
