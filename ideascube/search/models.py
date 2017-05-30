from django.db import models
from django.db.backends.signals import connection_created
from django.db.models.signals import class_prepared, post_save, pre_delete
from django.db.models.base import ModelBase
from django.dispatch import receiver

from .utils import rank
from ..utils import MetaRegistry


class Match(models.Lookup):
    lookup_name = 'match'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '{0} MATCH {1}'.format(lhs, rhs), params


class SearchField(models.Field):
    pass
SearchField.register_lookup(Match)


class TagMatch(models.Lookup):
    lookup_name = 'match'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        params = params[0]
        if not params:
            # Not tags to match to.
            # Search for stuff with no tag
            params = ['']
        out = '({0} LIKE {1})'.format(lhs, rhs)
        out = ' AND '.join([out]*len(params))
        out = '({})'.format(out)
        return out, ['%|{}|%'.format(p.lower()) for p in params]


class SearchTagField(models.Field):
    pass
SearchTagField.register_lookup(TagMatch)


class SearchQuerySet(models.QuerySet):
    def order_by_relevancy(self):
        extra = {'relevancy': 'rank(matchinfo(idx))'}
        return self.extra(select=extra).order_by('-relevancy')


class Search(models.Model):
    """Model that handle the search."""
    rowid = models.IntegerField(primary_key=True)
    model = models.CharField(max_length=64)
    model_id = models.IntegerField()
    public = models.BooleanField(default=True)
    text = SearchField()
    lang = models.Field()
    kind = models.Field()
    tags = SearchTagField()
    source = models.Field()

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
        return (SearchMixin.registered_types[r.model].objects.get(pk=r.model_id) for r in qs)


class MetaSearchMixin(MetaRegistry, ModelBase):
    pass


class SearchMixin(models.Model, metaclass=MetaSearchMixin):
    """Inherit from this mixin to make your model searchable."""

    class Meta:
        abstract = True

    @property
    def index_strings(self):
        return []

    @property
    def index_lang(self):
        return None

    @property
    def index_kind(self):
        return None

    @property
    def index_tags(self):
        return []

    @property
    def index_public(self):
        return True

    @property
    def index_source(self):
        return None

    def is_indexable(self):
        return True

    def index(self):
        if not self.is_indexable():
            return
        text = u" ".join([s for s in self.index_strings if s])
        tags = u"|{}|".format(u"|".join(self.index_tags))
        defaults = {
            'text': text,
            'public': self.index_public,
            'lang': self.index_lang,
            'kind': self.index_kind,
            'source': self.index_source,
            'tags': tags
        }
        Search.objects.update_or_create(
            model=self.__class__.__name__,
            model_id=self.pk,
            defaults=defaults
        )

    def deindex(self):
        Search.objects.filter(
            model=self.__class__.__name__,
            model_id=self.pk).delete()


class SearchableQuerySet(object):
    def search(self, query=None, kind=None, lang=None, tags=[], source=None, **kwargs):
        kwargs['model'] = self.model.__name__
        if query:
            kwargs['text__match'] = query
        if kind:
            kwargs['kind'] = kind
        if lang:
            kwargs['lang'] = lang
        if source:
            kwargs['source'] = source
        if tags:
            kwargs['tags__match'] = tags
        ids = Search.ids(**kwargs).distinct()
        # Force the execution of the request here
        # as we can request on several db in the same time.
        ids = list(ids)
        return self.filter(pk__in=ids)


@receiver(post_save)
def index(sender, instance, **kwargs):
    if issubclass(sender, SearchMixin):
        instance.index()


@receiver(pre_delete)
def deindex(sender, instance, **kwargs):
    if issubclass(sender, SearchMixin):
        instance.deindex()


@receiver(connection_created)
def add_rank_function(sender, connection, **kwargs):
    connection.connection.create_function("rank", 1, rank)
