import argparse
import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand

from ideascube.management.utils import Reporter
from ideascube.serveradmin.catalog import Catalog


class Command(BaseCommand):
    help = 'Manage apps and content'

    def add_arguments(self, parser):
        subs = parser.add_subparsers(
            title='Commands', dest='cmd', metavar='command')
        subs.required = True

        required_ids = argparse.ArgumentParser('common_stuff', add_help=False)
        required_ids.add_argument('ids', nargs='+', help='One or more package ids')

        optional_ids = argparse.ArgumentParser('common_stuff', add_help=False) 
        optional_ids.add_argument('ids', nargs='*', help='Optional package ids')

        install_parser = subs.add_parser('install', cmd=self, help='Install packages', parents=[required_ids])
        install_parser.set_defaults(func=self.install)

        remove_parser = subs.add_parser('remove', cmd=self, help='Remove packages', parents=[required_ids])
        remove_parser.set_defaults(func=self.remove)

        upgrade_parser = subs.add_parser('upgrade', cmd=self, help='Upgrade packages', parents=[optional_ids])
        upgrade_parser.set_defaults(func=self.upgrade)

        list_parser = subs.add_parser('list', cmd=self, help='List packages')
        list_parser.add_argument('--installed', action='store_true', help='List installed packages')
        list_parser.add_argument('--available', action='store_true', help='List available packages')
        list_parser.set_defaults(func=self.list)

    def handle(self, *args, **options):
        catalog = Catalog(['./ideascube/serveradmin/tests/data/catalog.yml'])
        catalog.update()

        options['func'](catalog, options)

    def install(self, catalog, options):
        catalog.install(options['ids'])

    def remove(self, catalog, options):
        catalog.remove(options['ids'])

    def upgrade(self, catalog, options):
        catalog.upgrade(options['ids'])

    def list(self, catalog, options):
        if options['available']:
            catalog.list_available()

        elif options['installed']:
            catalog.list_installed()
