from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _


from ideasbox.models import TimeStampedModel


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(
            status=Content.PUBLISHED)


class DraftManager(models.Manager):
    def get_queryset(self):
        return super(DraftManager, self).get_queryset().filter(
            status=Content.DRAFT)


class DeletedManager(models.Manager):
    def get_queryset(self):
        return super(DeletedManager, self).get_queryset().filter(
            status=Content.DELETED)


class Content(TimeStampedModel, models.Model):

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

    objects = models.Manager()
    published = PublishedManager()
    draft = DraftManager()
    deleted = DeletedManager()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:content_detail', kwargs={'pk': self.pk})

    def get_author_display(self):
        return self.author_text or unicode(self.author)
