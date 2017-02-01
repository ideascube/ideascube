from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from taggit.managers import TaggableManager

from ideascube.models import (
    LanguageField, SortedTaggableManager, TimeStampedModel)
from ideascube.search.models import SearchableQuerySet, SearchMixin


class DocumentQuerySet(SearchableQuerySet, models.QuerySet):
    def image(self):
        return self.filter(kind=Document.IMAGE)

    def video(self):
        return self.filter(kind=Document.VIDEO)

    def pdf(self):
        return self.filter(kind=Document.PDF)

    def text(self):
        return self.filter(kind=Document.TEXT)

    def audio(self):
        return self.filter(kind=Document.AUDIO)


class Document(SearchMixin, TimeStampedModel):

    IMAGE = 'image'
    VIDEO = 'video'
    PDF = 'pdf'
    EPUB = 'epub'
    TEXT = 'text'
    AUDIO = 'audio'
    APP = 'app'
    OTHER = 'other'

    KIND_CHOICES = (
        (IMAGE, _('image')),
        (AUDIO, _('sound')),
        (VIDEO, _('video')),
        (PDF, _('pdf')),
        (TEXT, _('text')),
        (EPUB, _('epub')),
        (APP, _('app')),
        (OTHER, _('other')),
    )

    KIND_DICT = dict(KIND_CHOICES)

    title = models.CharField(verbose_name=_('title'), max_length=100)
    summary = models.TextField(verbose_name=_('summary'))
    lang = LanguageField(verbose_name=_('Language'), max_length=10, blank=True)
    original = models.FileField(verbose_name=_('original'),
                                upload_to='mediacenter/document',
                                max_length=10240)
    preview = models.ImageField(verbose_name=_('preview'),
                                upload_to='mediacenter/preview',
                                max_length=10240,
                                blank=True)
    credits = models.CharField(verbose_name=_('Authorship'), max_length=300)
    kind = models.CharField(verbose_name=_('type'),
                            max_length=5,
                            choices=KIND_CHOICES,
                            default=OTHER)

    objects = DocumentQuerySet.as_manager()
    tags = TaggableManager(verbose_name=_('Topics'),
                           blank=True,
                           manager=SortedTaggableManager)

    package_id = models.CharField(verbose_name=_('package'), max_length=100,
                                  blank=True)

    class Meta:
        ordering = ["-modified_at", ]

    def __str__(self):
        return self.title

    def __repr__(self):
        return '<{}: {}>'.format(self.kind, str(self))

    def get_absolute_url(self):
        return reverse('mediacenter:document_detail', kwargs={'pk': self.pk})

    @property
    def index_strings(self):
        return (self.title, self.summary, self.credits,
                u' '.join(self.tags.names()))

    @property
    def index_lang(self):
        return self.lang

    @property
    def index_kind(self):
        return self.kind

    @property
    def index_source(self):
        return self.package_id

    @property
    def index_tags(self):
        return self.tags.slugs()

    @property
    def slug(self):
        return self.get_kind_display()
