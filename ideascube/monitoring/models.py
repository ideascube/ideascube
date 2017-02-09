from datetime import date, datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ideascube.models import TimeStampedModel


class Entry(TimeStampedModel):
    CINEMA = 'cinema'
    LIBRARY = 'library'
    DIGITAL = 'digital'
    MODULES = (
        (CINEMA, _('Cinema')),
        (LIBRARY, _('Library')),
        (DIGITAL, _('Multimedia')),
    )
    module = models.CharField(verbose_name=_('module'),
                              max_length=20, choices=MODULES)
    activity = models.CharField(verbose_name=_('activity'),
                                max_length=200, blank=True)
    partner = models.CharField(verbose_name=_('partner'),
                               max_length=200, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name=_('user'))

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
    made_at = models.DateField(verbose_name=_('date'))
    comments = models.TextField(verbose_name=_('comments'), blank=True)

    def get_absolute_url(self):
        return reverse('monitoring:inventory', kwargs={'pk': self.pk})

    @property
    def specimens(self):
        return self.inventoryspecimen_set.all()

    def __contains__(self, specimen):
        return self.inventoryspecimen_set.filter(specimen=specimen).exists()


class StockItemQuerySet(models.QuerySet):
    def physical(self):
        return [item for item in self if item.instance.physical]


class StockItem(models.Model):
    physical = True
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
    module = models.CharField(verbose_name=_('module'), max_length=20,
                              choices=MODULES)
    name = models.CharField(verbose_name=_('name'), max_length=300)
    description = models.TextField(verbose_name=_('description'), blank=True)

    objects = StockItemQuerySet.as_manager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '{url}#stockitem-{pk}'.format(
            url=reverse('monitoring:stock'),
            pk=self.pk
        )

    @property
    def instance(self):
        if hasattr(self, 'book'):
            return self.book
        return self

    class Meta:
        ordering = ('module', 'name')


class SpecimenQuerySet(models.QuerySet):

    def physical(self):
        return [specimen.instance for specimen in self
                if specimen.instance.physical]

    def digital(self):
        return [specimen.instance for specimen in self
                if not specimen.instance.physical]


class Specimen(models.Model):
    physical = True

    # This is the barcode added by the staff (usually as a sticker)
    barcode = models.CharField(verbose_name=_('ideascube bar code'),
                               max_length=40,
                               unique=True, blank=True, null=True)
    # This is the serial number attributed by the manufacturer/distributor
    serial = models.CharField(verbose_name=_('Serial number'), max_length=100,
                              unique=True, blank=True, null=True)
    item = models.ForeignKey(StockItem, related_name='specimens',
                             verbose_name=_('item'))
    count = models.IntegerField(verbose_name=_('quantity'), default=1)
    comments = models.TextField(verbose_name=_('comments'), blank=True)

    objects = SpecimenQuerySet.as_manager()

    def get_absolute_url(self):
        return self.item.get_absolute_url()

    @property
    def instance(self):
        if hasattr(self, 'bookspecimen'):
            return self.bookspecimen
        return self

    class Meta:
        ordering = ('barcode', )


class InventorySpecimen(models.Model):
    inventory = models.ForeignKey(Inventory)
    specimen = models.ForeignKey(Specimen)
    count = models.IntegerField(default=1)

    class Meta:
        unique_together = ('inventory', 'specimen')


class LoanQuerySet(models.QuerySet):

    def due(self):
        return self.filter(returned_at__isnull=True)

    def returned(self):
        return self.filter(returned_at__isnull=False)


class Loan(TimeStampedModel):
    specimen = models.ForeignKey(Specimen, verbose_name=_('specimen'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='loans',
                             verbose_name=_('user'))
    by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='loans_made',
                           verbose_name=_('by'))
    due_date = models.DateField(verbose_name=_('Due date'), default=date.today)
    returned_at = models.DateTimeField(verbose_name=_('Return time'),
                                       default=None,
                                       null=True, blank=True)
    comments = models.CharField(verbose_name=_('Comments'), blank=True,
                                max_length=500)

    objects = LoanQuerySet.as_manager()

    @property
    def due(self):
        return self.returned_at is None

    def mark_returned(self):
        self.returned_at = datetime.now()
        self.save()

    class Meta:
        ordering = ('due_date', 'created_at')
