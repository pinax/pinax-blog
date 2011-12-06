import datetime

from django.conf import settings
from django.db import models


class PostManager(models.Manager):
    
    def published(self):
        qs = self.exclude(published=None)
        qs = qs.exclude(published__gt=datetime.datetime.now())
        #qs = qs.filter(sites=settings.SITE_ID)
        return qs
    
    def current(self):
        return self.published().order_by("-published")
