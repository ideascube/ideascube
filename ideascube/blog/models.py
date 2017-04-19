from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager
from taggit.models import TagBase
from unidecode import unidecode

from ideascube.models import (
    LanguageField, SortedTaggableManager, TimeStampedModel)
from ideascube.search.models import SearchableQuerySet, SearchMixin


# Monkeypatch TagBase.slugify, see:
# https://github.com/ideascube/ideascube/issues/118
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

    title = models.CharField(verbose_name=_('title'), max_length=100)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.PROTECT,
                               verbose_name=_('author'))
    summary = models.CharField(
        verbose_name=_('summary'), max_length=300, blank=True)
    image = models.ImageField(verbose_name=_('image'),
                              upload_to='blog/image',
                              blank=True)
    text = models.TextField(verbose_name=_('text'))
    published_at = models.DateTimeField(verbose_name=_('publication date'),
                                        default=timezone.now)
    status = models.PositiveSmallIntegerField(verbose_name=_('Status'),
                                              choices=STATUSES,
                                              default=DRAFT)
    lang = LanguageField(verbose_name=_('Language'), max_length=10,
                         default=settings.LANGUAGE_CODE)

    objects = ContentQuerySet.as_manager()
    tags = TaggableManager(blank=True, manager=SortedTaggableManager)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:content_detail', kwargs={'pk': self.pk})

    @property
    def index_strings(self):
        return (self.title, self.text, str(self.author),
                u' '.join(self.tags.names()))

    @property
    def index_public(self):
        return self.status == self.PUBLISHED

    @property
    def index_tags(self):
        return self.tags.slugs()

    @property
    def index_lang(self):
        return self.lang
