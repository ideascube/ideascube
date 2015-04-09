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


# Create your models here.
class Book(SearchMixin, TimeStampedModel):

    OTHER = 99
    # We deleted the 'digital' category  
    SECTION_CHOICES = (
        (1, _('children - cartoons')),
        (2, _('children - novels')),
        (3, _('children - documentary')),
        (4, _('children - comics')),
        (5, _('adults - novels')),
        (6, _('adults - documentary')),
        (7, _('adults - comics')),
        (8, _('game')),
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
    location = models.CharField(_('location'), max_length=300, blank=True)
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
                self.summary, self.serie)


class BookSpecimen(TimeStampedModel):

    book = models.ForeignKey(Book, related_name='specimens')
    serial = models.CharField(_('serial'), max_length=40, null=True, blank=True, unique=True)
    remarks = models.TextField(_('remarks'), blank=True)

    def __unicode__(self):
        return u'Specimen {0} of "{1}"'.format(self.serial, self.book)

    def get_absolute_url(self):
        return reverse('library:book_detail', kwargs={'pk': self.book.pk})

class BookSpecimenDigital(TimeStampedModel):
#This creates the digital specimen field in the data base 
    book = models.ForeignKey(Book, related_name='specimens_digital')
    remarks = models.TextField(_('remarks'), blank=True)
    name = 'Digital Version' # There is no more "serial" field but a "name" field instead

    def __unicode__(self):
        return u'Specimen {0} of "{1}"'.format(self.name, self.book)

    def get_absolute_url(self):
        return reverse('library:book_detail', kwargs={'pk': self.book.pk})
