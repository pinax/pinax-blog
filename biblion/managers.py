from django.db import models
from django.db.models.query import Q

from biblion.exceptions import InvalidSection
from biblion.settings import ALL_SECTION_NAME


class PostManager(models.Manager):
    
    def published(self):
        return self.exclude(published=None)
    
    def current(self):
        return self.published().order_by("-published")
    
    def section(self, value, queryset=None):
        
        if queryset is None:
            queryset = self.published()
        
        if not value:
            return queryset
        else:
            sections = dict(
                [(v, k) for k, v in self.model.SECTION_CHOICES]
            )
            try:
                section = sections[value]
            except KeyError:
                raise InvalidSection
            return queryset.filter(
                Q(section=sections[ALL_SECTION_NAME]) | Q(section=section),
            )