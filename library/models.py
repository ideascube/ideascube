from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ideasbox.models import TimeStampedModel


class BookQuerySet(models.QuerySet):
    def available(self):
        return self.filter(specimen__isnull=False).distinct()


# Create your models here.
class Book(TimeStampedModel):

    SECTION_CHOICES = (
        (1, _('digital')),
        (2, _('children - cartoons')),
        (3, _('children - novels')),
        (4, _('children - documentary')),
        (5, _('children - comics')),
        (6, _('adults - novels')),
        (7, _('adults - documentary')),
        (8, _('adults - comics')),
        (9, _('game')),
        (10, _('other')),
    )

    isbn = models.CharField(max_length=40, unique=True, null=True, blank=True)
    authors = models.CharField(_('authors'), max_length=300, blank=True)
    serie = models.CharField(_('serie'), max_length=300, blank=True)
    title = models.CharField(_('title'), max_length=300)
    subtitle = models.CharField(_('subtitle'), max_length=300, blank=True)
    summary = models.TextField(_('summary'), blank=True)
    section = models.PositiveSmallIntegerField(_('section'),
                                               choices=SECTION_CHOICES)
    location = models.CharField(_('location'), max_length=300, blank=True,
                                default=settings.IDEASBOX_ID)
    lang = models.CharField(_('Language'), max_length=10,
                            choices=settings.LANGUAGES,
                            default=settings.LANGUAGE_CODE)
    cover = models.ImageField(_('cover'), upload_to='library/cover',
                              blank=True)

    objects = BookQuerySet.as_manager()

    class Meta:
        ordering = ('title', )

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('library:book_detail', kwargs={'pk': self.pk})


class BookSpecimen(TimeStampedModel):

    book = models.ForeignKey(Book, related_name='specimen')
    serial = models.CharField(max_length=40, unique=True)
    remarks = models.TextField(_('remarks'), blank=True)

    def __unicode__(self):
        return u'Specimen %s of "%s"' % (self.serial, self.book)

    def get_absolute_url(self):
        return reverse('library:book_detail', kwargs={'pk': self.book.pk})
