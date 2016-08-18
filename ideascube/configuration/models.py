from django.conf import settings
from django.db import models

from ideascube.models import JSONField


class Configuration(models.Model):
    class Meta:
        ordering = ['-date']

    namespace = models.CharField(max_length=40)
    key = models.CharField(max_length=40)
    value = JSONField()
    actor = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s.%s=%r' % (self.namespace, self.key, self.value)
