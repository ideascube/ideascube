from django.apps import AppConfig
from django.db.models.signals import post_migrate

from .utils import create_index_table


def create_index(sender, **kwargs):
    create_index_table()


class SearchConfig(AppConfig):
    name = 'ideasbox.search'
    verbose_name = 'Search'

    def ready(self):
        post_migrate.connect(create_index, sender=self)
