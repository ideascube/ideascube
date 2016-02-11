import argparse

from django.core.management.base import BaseCommand, CommandError

from ideascube.serveradmin.catalog import Catalog


class Command(BaseCommand):
    help = 'Manage apps and content'

    def add_arguments(self, parser):
        subs = parser.add_subparsers(
            title='Commands', dest='cmd', metavar='',
            parser_class=argparse.ArgumentParser)

        # -- Manage local cache -----------------------------------------------
        cache = subs.add_parser('cache', help='Manage cache')

        cachesubs = cache.add_subparsers(title='Commands', dest='cachecmd')
        cachesubs.required = True

        update = cachesubs.add_parser('update', help='Update the local cache')
        update.set_defaults(func=self.update_cache)

        clear = cachesubs.add_parser('clear', help='Clear the local cache')
        clear.set_defaults(func=self.clear_cache)

        # -- Manage remote sources --------------------------------------------
        remote = subs.add_parser('remotes', help='Manage remote sources')

        remotesubs = remote.add_subparsers(title='Commands', dest='remotecmd')
        remotesubs.required = True

        list = remotesubs.add_parser('list', help='List known remote sources')
        list.set_defaults(func=self.list_remotes)

        add = remotesubs.add_parser('add', help='Add a remote source')
        add.add_argument('id', help='The id for the new remote source')
        add.add_argument('name', help='The name for the new remote source')
        add.add_argument('url', help='The url for the new remote source')
        add.set_defaults(func=self.add_remote)

        rm = remotesubs.add_parser('remove', help='Remove a remote source')
        rm.add_argument('id', help='The id of the remote source to remove')
        rm.set_defaults(func=self.remove_remote)

        self.parser = parser

    def handle(self, *args, **options):
        if 'func' not in options:
            self.parser.print_help()
            self.parser.exit(1)

        self.catalog = Catalog()
        options['func'](options)

    # -- Manage local cache ---------------------------------------------------
    def update_cache(self, options):
        self.catalog.update_cache()

    def clear_cache(self, options):
        self.catalog.clear_cache()

    # -- Manage remote sources ------------------------------------------------
    def list_remotes(self, options):
        for remote in self.catalog.list_remotes():
            left = '[{0.id}] {0.name}'.format(remote)
            print('{0:>35} : {1.url}'.format(left, remote))

    def add_remote(self, options):
        try:
            self.catalog.add_remote(
                options['id'], options['name'], options['url'])

        except ValueError as e:
            raise CommandError(e)

        self.catalog.update_cache()

    def remove_remote(self, options):
        try:
            self.catalog.remove_remote(options['id'])

        except ValueError as e:
            raise CommandError(e)

        self.catalog.update_cache()
