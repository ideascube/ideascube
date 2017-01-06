
import os
import sys
import yaml
from datetime import date
from collections import OrderedDict

from ideascube.serveradmin.package import MediaCenterPackage
from ideascube.management.utils import Reporter
from ideascube.utils import get_file_sha256, get_file_size

from django.core.management.base import BaseCommand

help_str = """Convert a CSV describing a set of media into a package.

The CSV file must contain columns "title", "summary", "path" and "credits".
Optional columns are "lang", "preview", "kind", "tags".
Attributes "path" and "preview" (if provided) must be paths
(relative to the directory containing the CSV) to existing files.

csv2pkg also generates a yaml to add to the catalog.
Some attributes are automically calculated from the generated package.
Other attributes may be provided as command arguments.
"""


def ordered_representer(dumper, data):
    return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())

yaml.add_representer(OrderedDict, ordered_representer, Dumper=yaml.SafeDumper)


def generate_catalog_yaml_metadata(path, metadata, _type='zipped-medias'):
    return {
        'all' : {
            metadata['package_id']: OrderedDict([
                ('name', metadata['name']),
                ('description', metadata['description']),
                ('language', metadata['language']),
                ('version', date.today().isoformat()),
                ('url', metadata['url']),
                ('size', get_file_size(path)),
                ('sha256sum', get_file_sha256(path)),
                ('type', _type)
            ])
        }
    }


class Command(BaseCommand):
    help = help_str

    def add_arguments(self, parser):
        parser.add_argument('csv_path', help='Path to CSV metadata.')
        parser.add_argument('package_path',
                            help='Path of the package to create')
        parser.add_argument('--dry-run', action='store_true',
                            help='Do not really create the package.')

        group = parser.add_argument_group('yaml generation arguments')
        group.add_argument('--package-id', default="<package_id>",
                           help="Identifier of the package.")
        group.add_argument('--name', default="<Package name>",
                           help="Name of the package.")
        group.add_argument('--description', default="<Package description>",
                           help="Description of the package.")
        group.add_argument('--language', default="<lang>",
                           help="Language of the package.")
        group.add_argument('--url', default="<http://...>",
                           help="URL where the package will be available")

    def abort(self, msg):
        self.stderr.write(msg)
        sys.exit(1)

    def handle(self, *args, **options):
        report = Reporter(options['verbosity'])
        csv_path = os.path.abspath(options['csv_path'])
        package_path = os.path.abspath(options['package_path'])

        if options['dry_run']:
            print("--dry-run option given, no package will be created")

        if not os.path.exists(csv_path):
            self.abort('Path does not exist: {}'.format(csv_path))
        os.makedirs(os.path.dirname(package_path), exist_ok=True)

        package = MediaCenterPackage.from_csv(csv_path, report=report)
        print(report)

        if not package.medias:
            self.abort("There is no (valid) media to create the package.\n"
                       "No package will be created")
        elif not options['dry_run']:
            package.create_package_zip(package_path)

        print("\nPackage {package_path} {verb} been created with"
              " {nb_media} medias."
              .format(
                  verb="would have" if options['dry_run'] else "has",
                  package_path=package_path,
                  nb_media=len(package.medias)
                  )
              )

        if not options['dry_run']:
            print("\nYaml to use is: \n")
            yaml_metadata = generate_catalog_yaml_metadata(
                package_path, options)
            print(yaml.safe_dump(yaml_metadata, default_flow_style=False))
