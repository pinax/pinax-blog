from django.db import models
from django.db.models.query import Q

from biblion.exceptions import InvalidSection


class PostManager(models.Manager):
    
    def published(self):
        return self.exclude(published=None)
    
    def current(self):
        return self.published().order_by("-published")
    
    def section(self, value):
        
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
                Q(section=sections["general"]) | Q(section=section),
            )