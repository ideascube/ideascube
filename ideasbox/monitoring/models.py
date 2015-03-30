from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext as _

from ideasbox.models import TimeStampedModel


class Entry(TimeStampedModel):
    CINEMA = 'cinema'
    LIBRARY = 'library'
    DIGITAL = 'digital'
    MODULES = (
        (CINEMA, _('Cinema')),
        (LIBRARY, _('Library')),
        (DIGITAL, _('Multimedia')),
    )
    module = models.CharField(max_length=20, choices=MODULES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

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


class Inventory(TimeStampedModel):
    made_at = models.DateField(_('date'))
    comments = models.TextField(_('comments'), blank=True)

    def get_absolute_url(self):
        return reverse('monitoring:inventory', kwargs={'pk': self.pk})

    @property
    def specimens(self):
        return self.inventoryspecimen_set.all()

    def __contains__(self, specimen):
        return self.inventoryspecimen_set.filter(specimen=specimen).exists()


class StockItem(models.Model):
    CINEMA = 'cinema'
    LIBRARY = 'library'
    DIGITAL = 'digital'
    ADMIN = 'admin'
    OTHER = 'other'
    MODULES = (
        (CINEMA, _('Cinema')),
        (LIBRARY, _('Library')),
        (DIGITAL, _('Multimedia')),
        (ADMIN, _('Administration')),
        (OTHER, _('Other')),
    )
    module = models.CharField(max_length=20, choices=MODULES)
    name = models.CharField(_('name'), max_length=150)
    description = models.TextField(_('description'), blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return '{url}#stockitem-{pk}'.format(
            url=reverse('monitoring:stock'),
            pk=self.pk
        )

    class Meta:
        ordering = ('module', 'name')


class Specimen(models.Model):
    barcode = models.CharField(_('Ideasbox bar code'), max_length=40,
                               unique=True, blank=True, null=True)
    serial = models.CharField(_('Serial number'), max_length=100, blank=True,
                              null=True)
    item = models.ForeignKey(StockItem, related_name='specimens')
    count = models.IntegerField(default=1)
    comments = models.TextField(_('comments'), blank=True)

    def get_absolute_url(self):
        return self.item.get_absolute_url()


class InventorySpecimen(models.Model):
    inventory = models.ForeignKey(Inventory)
    specimen = models.ForeignKey(Specimen)
    count = models.IntegerField(default=1)

    class Meta:
        unique_together = ('inventory', 'specimen')
