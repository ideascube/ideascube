from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from taggit.managers import TaggableManager

from ideascube.models import SortedTaggableManager, TimeStampedModel
from ideascube.search.models import SearchableQuerySet, SearchMixin
from .utils import guess_kind_from_filename


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

    title = models.CharField(_('title'), max_length=100)
    summary = models.TextField(_('summary'))
    lang = models.CharField(_('Language'), max_length=10, blank=True,
                            choices=settings.LANGUAGES)
    original = models.FileField(_('original'),
                                upload_to='mediacenter/document',
                                max_length=10240)
    preview = models.ImageField(_('preview'),
                                upload_to='mediacenter/preview',
                                max_length=10240,
                                blank=True)
    credits = models.CharField(_('credit'), max_length=300)
    kind = models.CharField(_('type'), max_length=5, choices=KIND_CHOICES,
                            default=OTHER)

    objects = DocumentQuerySet.as_manager()
    tags = TaggableManager(blank=True, manager=SortedTaggableManager)

    package_id = models.CharField(_('package_id'), max_length=100, blank=True)

    class Meta:
        ordering = ["-modified_at", ]

    def __str__(self):
        return self.title

    def __repr__(self):
        return '<{}: {}>'.format(self.kind, str(self))

    def get_absolute_url(self):
        return reverse('mediacenter:document_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        self.set_kind()
        super(Document, self).save(*args, **kwargs)

    def set_kind(self):
        """Set Document kind guessing from the file name. If kind is already
        set, does nothing."""
        if self.original and (not self.kind or self.kind == self.OTHER):
            kind = guess_kind_from_filename(self.original.name)
            if kind:
                self.kind = kind

    @property
    def index_strings(self):
        return (self.title, self.summary, self.credits,
                u' '.join(self.tags.names()))

    @property
    def slug(self):
        return self.get_kind_display()
