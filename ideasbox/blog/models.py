from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager
from taggit.models import TagBase
from unidecode import unidecode

from ideasbox.models import TimeStampedModel
from ideasbox.search.models import SearchableQuerySet, SearchMixin


# Monkeypatch TagBase.slugify, see:
# https://github.com/ideas-box/ideasbox.lan/issues/118
original_slugify = TagBase.slugify


def custom_slugify(self, tag, i=None):
    tag = unidecode(tag)
    return original_slugify(self, tag, i)

TagBase.slugify = custom_slugify


class ContentQuerySet(SearchableQuerySet, models.QuerySet):
    def published(self):
        return self.filter(status=Content.PUBLISHED,
                           published_at__lt=timezone.now())

    def draft(self):
        return self.filter(status=Content.DRAFT)

    def deleted(self):
        return self.filter(status=Content.DELETED)


class Content(SearchMixin, TimeStampedModel, models.Model):

    DRAFT = 1
    PUBLISHED = 2
    DELETED = 3
    STATUSES = (
        (DRAFT, _('draft')),
        (PUBLISHED, _('published')),
        (DELETED, _('deleted')),
    )

    title = models.CharField(_('title'), max_length=100)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    author_text = models.CharField(_('author text'), max_length=300,
                                   blank=True)
    summary = models.CharField(_('summary'), max_length=300)
    image = models.ImageField(_('image'), upload_to='blog/image', blank=True)
    text = models.TextField(_('text'))
    published_at = models.DateTimeField(_('publication date'))
    status = models.PositiveSmallIntegerField(_('Status'), choices=STATUSES,
                                              default=DRAFT)
    lang = models.CharField(_('Language'), max_length=10,
                            choices=settings.LANGUAGES,
                            default=settings.LANGUAGE_CODE)

    objects = ContentQuerySet.as_manager()
    tags = TaggableManager(blank=True)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:content_detail', kwargs={'pk': self.pk})

    def get_author_display(self):
        return self.author_text or unicode(self.author)

    @property
    def index_strings(self):
        return (self.title, self.text, self.author_text, unicode(self.author),
                u' '.join(self.tags.names()))

    @property
    def index_public(self):
        return self.status == self.PUBLISHED
