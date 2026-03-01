from django.db import models
from django.utils import timezone


class PublishedPostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )
