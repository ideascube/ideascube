from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ideasbox.models import TimeStampedModel
from search.models import SearchableQuerySet, SearchMixin
from .utils import guess_type


class DocumentQuerySet(SearchableQuerySet, models.QuerySet):
    def image(self):
        return self.filter(type=Document.IMAGE)

    def video(self):
        return self.filter(type=Document.VIDEO)

    def pdf(self):
        return self.filter(type=Document.PDF)

    def text(self):
        return self.filter(type=Document.TEXT)

    def audio(self):
        return self.filter(type=Document.AUDIO)


class Document(SearchMixin, TimeStampedModel, models.Model):

    IMAGE = 'image'
    VIDEO = 'video'
    PDF = 'pdf'
    TEXT = 'text'
    AUDIO = 'audio'
    OTHER = 'other'

    TYPE_CHOICES = (
        (IMAGE, _('image')),
        (AUDIO, _('sound')),
        (VIDEO, _('video')),
        (PDF, _('pdf')),
        (TEXT, _('text')),
        (OTHER, _('other')),
    )

    title = models.CharField(_('title'), max_length=100)
    summary = models.TextField(_('summary'))
    lang = models.CharField(_('Language'), max_length=10, blank=True,
                            choices=settings.LANGUAGES)
    original = models.FileField(_('original'),
                                upload_to='mediacenter/document')
    preview = models.ImageField(_('preview'), upload_to='mediacenter/preview',
                                blank=True)
    credits = models.CharField(_('credit'), max_length=300)
    type = models.CharField(_('type'), max_length=5, choices=TYPE_CHOICES,
                            default=OTHER)

    objects = DocumentQuerySet.as_manager()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('mediacenter:document_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        self.set_type()
        super(Document, self).save(*args, **kwargs)

    def set_type(self):
        if self.original and (not self.type or self.type == self.OTHER):
            _type = guess_type(self.original.name)
            if _type:
                self.type = _type

    @property
    def index_strings(self):
        return (self.title, self.summary, self.credits)
