from django.core.management.base import BaseCommand

from ideastube.search.utils import create_index_table
from ideastube.search.models import SEARCHABLE


class Command(BaseCommand):
    help = 'Reindex all the searchable objects'

    def handle(self, *args, **kwargs):
        create_index_table()
        for model in SEARCHABLE.values():
            count = 0
            for inst in model.objects.all():
                inst.index()
                count += 1
            if count:
                self.stdout.write('Indexed {} content.'.format(model.__name__))
        self.stdout.write('Done reindexing.')
