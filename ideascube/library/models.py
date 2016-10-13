import os

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager

from ideascube.models import (
    LanguageField, SortedTaggableManager, TimeStampedModel)
from ideascube.monitoring.models import StockItem, Specimen
from ideascube.search.models import SearchableQuerySet, SearchMixin


class BookQuerySet(SearchableQuerySet, models.QuerySet):
    def available(self):
        return self.filter(specimens__isnull=False).distinct()


class Book(StockItem, SearchMixin, TimeStampedModel):

    OTHER = 99

    SECTION_CHOICES = (
        (1, _('digital')),
        (2, _('children - cartoons')),
        (3, _('children - novels')),
        (10, _('children - poetry')),
        (11, _('children - theatre')),
        (4, _('children - documentary')),
        (5, _('children - comics')),
        (6, _('adults - novels')),
        (12, _('adults - poetry')),
        (13, _('adults - theatre')),
        (7, _('adults - documentary')),
        (8, _('adults - comics')),
        (9, _('game')),
        (OTHER, _('other')),
    )

    # We allow ISBN to be null, but when it is set it needs to be unique.
    isbn = models.CharField(verbose_name=_('isbn'), max_length=40,
                            unique=True, null=True, blank=True)
    authors = models.CharField(verbose_name=_('authors'), max_length=300,
                               blank=True)
    serie = models.CharField(verbose_name=_('serie'), max_length=300,
                             blank=True)
    subtitle = models.CharField(verbose_name=_('subtitle'), max_length=300,
                                blank=True)
    publisher = models.CharField(verbose_name=_('publisher'), max_length=100,
                                 blank=True)
    section = models.PositiveSmallIntegerField(verbose_name=_('section'),
                                               choices=SECTION_CHOICES)
    lang = LanguageField(verbose_name=_('Language'), max_length=10)
    cover = models.ImageField(verbose_name=_('cover'),
                              upload_to='library/cover',
                              blank=True)

    objects = BookQuerySet.as_manager()
    tags = TaggableManager(blank=True, manager=SortedTaggableManager)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('library:book_detail', kwargs={'pk': self.pk})

    @property
    def index_strings(self):
        return (self.name, self.isbn, self.authors, self.subtitle,
                self.description, self.serie, u' '.join(self.tags.names()))

    @property
    def index_tags(self):
        return self.tags.slugs()

    @property
    def index_lang(self):
        return self.lang

    @property
    def physical(self):
        return any(s.instance.physical for s in self.specimens.all())

    def save(self, *args, **kwargs):
        self.module = self.LIBRARY
        return super().save(*args, **kwargs)


class BookSpecimen(Specimen, TimeStampedModel):

    location = models.CharField(verbose_name=_('location'), max_length=300,
                                blank=True)
    file = models.FileField(verbose_name=_('digital file'),
                            upload_to='library/digital',
                            blank=True)

    @property
    def physical(self):
        return not bool(self.file)

    def __str__(self):
        if self.physical:
            # barcode is null for digital specimens.
            return u'Specimen {0} of "{1}"'.format(self.barcode, self.item)
        return u'Digital specimen of "{0}"'.format(self.item)

    def get_absolute_url(self):
        return reverse('library:book_detail', kwargs={'pk': self.item.pk})

    @property
    def extension(self):
        if not self.file:
            return ''
        name, extension = os.path.splitext(self.file.name)
        return extension[1:]
