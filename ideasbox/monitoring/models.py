from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

from ideasbox.models import TimeStampedModel


class Entry(TimeStampedModel):

    MODULES = (
        ('cinema', _('Cinema')),
        ('library', _('Library')),
        ('digital', _('Digital')),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    module = models.CharField(max_length=20, choices=MODULES)

    class Meta:
        verbose_name = _("entry")
        verbose_name_plural = _("entries")
        ordering = ('-created_at',)

    def __str__(self):
        return 'Entry of {user} in {module} module on {date}'.format(
            user=self.user,
            module=self.module,
            date=self.created_at,
        )
