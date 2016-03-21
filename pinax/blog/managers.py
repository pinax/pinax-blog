from django.db import models
from django.utils import timezone

from .conf import settings


PUBLISHED_STATE = len(settings.PINAX_BLOG_UNPUBLISHED_STATES) + 1


class PostManager(models.Manager):

    def published(self):
        return self.filter(published__lte=timezone.now(), state=PUBLISHED_STATE)

    def current(self):
        return self.published().order_by("-published")
