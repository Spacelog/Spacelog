from django.contrib.postgres.fields import ArrayField
from django.db import models


class Mission(models.Model):
    name = models.CharField(max_length=10, unique=True)
    subdomains = ArrayField(models.CharField(max_length=63), db_index=True)
    utc_launch_time = models.DateTimeField()
    memorial = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    incomplete = models.BooleanField(default=True)
    main_transcript = models.CharField(max_length=20, null=True)
    media_transcript = models.CharField(max_length=20, null=True)

    @property
    def subdomain(self):
        return self.subdomains[0]
