
import os
import sys

from ideascube.serveradmin.package import MediaCenterPackage

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ('Convert a CSV describing a set of media into a package. '
            'The CSV file must contain columns "title", "summary", "path", '
            '"credits". Optional columns are "lang", "preview", "kind", "tags".'
            ' Attributes "path" and "preview" (if provided) must be path '
            '(relative to csv directory) to existing files.')

    def add_arguments(self, parser):
        parser.add_argument('csv_path', help='Path to CSV metadata.')
        parser.add_argument('package_path',
                            help='Path of the package to create')
        parser.add_argument('--dry-run', action='store_true',
                            help='Do not really create the package.')

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
        if not options['dry_run']:
            package.create_package_zip(package_path)
