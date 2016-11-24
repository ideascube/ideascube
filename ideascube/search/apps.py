from django.apps import AppConfig
from django.db.models.signals import pre_migrate, post_migrate

from .utils import create_index_table, reindex_content


def create_index(sender, **kwargs):
    if (kwargs['using'] == 'transient' and isinstance(sender, SearchConfig)):
        create_index_table(force=True)


def reindex(sender, **kwargs):
    if (kwargs['using'] == 'transient' and isinstance(sender, SearchConfig)):
        reindex_content(force=False)


class SearchConfig(AppConfig):
    name = 'ideascube.search'
    verbose_name = 'Search'

    def ready(self):
        pre_migrate.connect(create_index, sender=self)
        post_migrate.connect(reindex, sender=self)
