from django.core.management.base import BaseCommand


from blog.models import Content
from library.models import Book
from search.utils import create_index_table


class Command(BaseCommand):
    help = 'Reindex all the searchable objects'

    def handle(self, *args, **options):
        create_index_table()
        models = [Content, Book]
        for model in models:
            self.stdout.write('Indexing {} content.'.format(model.__name__))
            for inst in model.objects.all():
                inst.index()
        self.stdout.write('Done reindexing.')
