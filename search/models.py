from django.db import models
from django.db.backends.signals import connection_created
from django.db.models.signals import class_prepared, post_save, pre_delete
from django.dispatch import receiver
from django.utils.module_loading import import_string

from .utils import rank


class Match(models.Lookup):
    lookup_name = 'match'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s MATCH %s' % (lhs, rhs), params


class SearchField(models.Field):
    pass
SearchField.register_lookup(Match)


class SearchQuerySet(models.QuerySet):
    def order_by_relevancy(self):
        extra = {'relevancy': 'rank(matchinfo(idx))'}
        return self.extra(select=extra).order_by('-relevancy')


class Search(models.Model):
    """Model that handle the search."""
    rowid = models.IntegerField(primary_key=True)
    module = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    model_id = models.IntegerField()
    public = models.BooleanField(default=True)
    text = SearchField()

    objects = SearchQuerySet.as_manager()

    class Meta:
        db_table = 'idx'
        managed = False

    @classmethod
    def ids(cls, **kwargs):
        qs = Search.objects.filter(**kwargs).order_by_relevancy()
        return qs.values_list('model_id', flat=True)

    @classmethod
    def search(cls, **kwargs):
        qs = Search.objects.filter(**kwargs).order_by_relevancy()
        for row in qs:
            yield _SEARCHABLE[row.model].objects.get(pk=row.model_id)


class SearchMixin(models.Model):
    """Inherit from this mixin to make your model searchable."""

    class Meta:
        abstract = True

    @property
    def index_strings(self):
        return []

    @property
    def index_public(self):
        return True

    def is_indexable(self):
        return True

    def index(self):
        if not self.is_indexable():
            return
        text = u" ".join([s for s in self.index_strings if s])
        defaults = dict(text=text, public=self.index_public)
        Search.objects.update_or_create(
            module=self.__class__.__module__,
            model=self.__class__.__name__,
            model_id=self.pk,
            defaults=defaults
        )

    def deindex(self):
        Search.objects.filter(
            module=self.__class__.__module__,
            model=self.__class__.__name__,
            model_id=self.pk).delete()


class SearchableQuerySet(object):
    def search(self, query, **kwargs):
        kwargs['text__match'] = query
        kwargs['model'] = self.model.__name__
        ids = Search.ids(**kwargs)
        return self.filter(pk__in=ids)


@receiver(post_save)
def index(sender, instance, **kwargs):
    if SearchMixin in sender.__mro__:
        instance.index()


@receiver(pre_delete)
def deindex(sender, instance, **kwargs):
    if SearchMixin in sender.__mro__:
        instance.deindex()


@receiver(connection_created)
def add_rank_function(sender, connection, **kwargs):
    connection.connection.create_function("rank", 1, rank)


@receiver(class_prepared)
def register_searchable_model(sender, **kwargs):
    if SearchMixin in sender.__mro__:
        _SEARCHABLE[sender.__name__] = sender
_SEARCHABLE = {}
