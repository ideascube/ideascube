
import os
import sys

from ideascube.catalog_utils.package import MediaCenterPackage

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ('Batch import medias from CSV metadata. CSV file must contain '
            'columns "title", "summary", "path", "credits". Optional columns '
            'are "lang", "preview", "kind", "tags".')

    def add_arguments(self, parser):
        parser.add_argument('csv_path', help='Path to CSV metadata.')
        parser.add_argument('package_path',
                            help='Path of the package to create')

    def abort(self, msg):
        self.stderr.write(msg)
        sys.exit(1)

    def handle(self, *args, **options):
        csv_path = os.path.abspath(options['csv_path'])
        package_path = os.path.abspath(options['package_path'])

        if not os.path.exists(csv_path):
            self.abort('Path does not exist: {}'.format(csv_path))
        os.makedirs(os.path.dirname(package_path), exist_ok=True)

        package = MediaCenterPackage.from_csv(csv_path)
        package.create_package_zip(package_path)
