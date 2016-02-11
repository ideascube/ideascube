import argparse

from django.core.management.base import BaseCommand, CommandError

from ideascube.serveradmin.catalog import Catalog, NoSuchPackage


class Command(BaseCommand):
    help = 'Manage apps and content'

    def add_arguments(self, parser):
        subs = parser.add_subparsers(
            title='Commands', dest='cmd', metavar='',
            parser_class=argparse.ArgumentParser)

        required_ids = argparse.ArgumentParser('required_ids', add_help=False)
        required_ids.add_argument(
            'ids', nargs='+', metavar='ID',
            help='One or more package ids (or globs)')

        optional_ids = argparse.ArgumentParser('optional_ids', add_help=False)
        optional_ids.add_argument(
            'ids', nargs='*', metavar='ID', default=['*'],
            help='Optional package ids (or globs)')

        # -- Manage content ---------------------------------------------------
        list = subs.add_parser(
            'list', parents=[optional_ids], help='List packages')
        group = list.add_mutually_exclusive_group()
        group.add_argument(
            '--installed', action='store_const', dest='filter',
            const='installed', help='Only list installed packages')
        group.add_argument(
            '--available', action='store_const', dest='filter',
            const='available', help='Only list available packages')
        group.add_argument(
            '--upgradable', action='store_const', dest='filter',
            const='upgradable',
            help='Only list installed packages with updates available')
        group.add_argument(
            '--all', action='store_const', dest='filter', const='all',
            help='List available and installed packages (default)')
        list.set_defaults(filter='all', func=self.list_packages)

        install = subs.add_parser(
            'install', parents=[required_ids],
            help='Install packages')
        install.set_defaults(func=self.install_packages)

        remove = subs.add_parser(
            'remove', parents=[required_ids], help='Remove packages')
        remove.set_defaults(func=self.remove_packages)

        upgrade = subs.add_parser(
            'upgrade', aliases=['update'],
            parents=[optional_ids], help='Upgrade packages')
        upgrade.set_defaults(func=self.upgrade_packages)

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

    # -- Manage content -------------------------------------------------------
    def list_packages(self, options):
        fmt = ' {0.id:20}  {0.version:10}  {0.size:5}  {0.name}'

        if options['filter'] in ('all', 'installed'):
            pkgs = self.catalog.list_installed(options['ids'])

            if pkgs:
                print('Installed packages')

                for pkg in pkgs:
                    print(fmt.format(pkg))

        if options['filter'] in ('all', 'available'):
            pkgs = self.catalog.list_available(options['ids'])

            if pkgs:
                print('Available packages')

                for pkg in pkgs:
                    print(fmt.format(pkg))

        if options['filter'] == 'upgradable':
            pkgs = self.catalog.list_upgradable(options['ids'])

            if pkgs:
                print('Available updates')

                for pkg in pkgs:
                    print(fmt.format(pkg))

    def install_packages(self, options):
        try:
            self.catalog.install_packages(options['ids'])

        except NoSuchPackage as e:
            raise CommandError('No such package: {}'.format(e))

    def remove_packages(self, options):
        try:
            self.catalog.remove_packages(options['ids'])

        except NoSuchPackage as e:
            raise CommandError('No such package: {}'.format(e))

    def upgrade_packages(self, options):
        try:
            self.catalog.upgrade_packages(options['ids'])

        except NoSuchPackage as e:
            raise CommandError('No such package: {}'.format(e))

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
