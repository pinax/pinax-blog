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
            try:
                section_idx = self.model.section_idx(value)
            except KeyError:
                raise InvalidSection
            all_sections = Q(section=self.model.section_idx(ALL_SECTION_NAME))
            return queryset.filter(all_sections | Q(section=section_idx))