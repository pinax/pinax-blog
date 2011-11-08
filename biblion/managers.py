import datetime

from django.db import models


class PostManager(models.Manager):
    
    def published(self):
        return self.exclude(
            published=None
        ).exclude(
            published__gt=datetime.datetime.now()
        )
    
    def current(self):
        return self.published().order_by("-published")
