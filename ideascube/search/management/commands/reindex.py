from django.core.management.base import BaseCommand

from ideascube.search.utils import reindex_content


class Command(BaseCommand):
    help = 'Reindex all the searchable objects'

    def handle(self, *args, **kwargs):
        indexed = reindex_content()
        for name, count in indexed.items():
            if count:
                self.stdout.write('Indexed {} content.'.format(name))
        self.stdout.write('Done reindexing.')
