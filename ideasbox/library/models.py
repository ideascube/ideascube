from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from taggit.managers import TaggableManager

from ideasbox.models import TimeStampedModel
from ideasbox.search.models import SearchableQuerySet, SearchMixin


class BookQuerySet(SearchableQuerySet, models.QuerySet):
    def available(self):
        return self.filter(specimens__isnull=False).distinct()


class Book(SearchMixin, TimeStampedModel):

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
    isbn = models.CharField(max_length=40, unique=True, null=True, blank=True)
    authors = models.CharField(_('authors'), max_length=300, blank=True)
    serie = models.CharField(_('serie'), max_length=300, blank=True)
    title = models.CharField(_('title'), max_length=300)
    subtitle = models.CharField(_('subtitle'), max_length=300, blank=True)
    summary = models.TextField(_('summary'), blank=True)
    publisher = models.CharField(_('publisher'), max_length=100, blank=True)
    section = models.PositiveSmallIntegerField(_('section'),
                                               choices=SECTION_CHOICES)
    lang = models.CharField(_('Language'), max_length=10,
                            choices=settings.LANGUAGES)
    cover = models.ImageField(_('cover'), upload_to='library/cover',
                              blank=True)

    objects = BookQuerySet.as_manager()
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('library:book_detail', kwargs={'pk': self.pk})

    @property
    def index_strings(self):
        return (self.title, self.isbn, self.authors, self.subtitle,
                self.summary, self.serie, u' '.join(self.tags.names()))


class BookSpecimen(TimeStampedModel):

    book = models.ForeignKey(Book, related_name='specimens')
    serial = models.CharField(_('serial'), max_length=40, unique=True,
                              blank=True, null=True)
    location = models.CharField(_('location'), max_length=300, blank=True)
    remarks = models.TextField(_('remarks'), blank=True)
    file = models.FileField(_('digital file'), upload_to='library/digital',
                            blank=True)

    @property
    def is_digital(self):
        return bool(self.file)

    def __unicode__(self):
        if self.is_digital:
            # serial is null for digital specimens.
            return u'Digital specimen of "{0}"'.format(self.book)
        return u'Specimen {0} of "{1}"'.format(self.serial, self.book)

    def get_absolute_url(self):
        return reverse('library:book_detail', kwargs={'pk': self.book.pk})
