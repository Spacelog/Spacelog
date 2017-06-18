from django.contrib.postgres.fields import ArrayField, JSONField
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
    copy = JSONField(default={})

    @property
    def subdomain(self):
        return self.subdomains[0]

    @property
    def title(self):
        return self.copy['title']

    @property
    def upper_title(self):
        return self.copy['upper_title']

    @property
    def lower_title(self):
        return self.copy['lower_title']

    @property
    def summary(self):
        return self.copy.get('summary', '')

    @property
    def description(self):
        return self.copy.get('description', self.summary)

    @property
    def type_search(self):
        return self.copy.get('type_search', 'reentry')
