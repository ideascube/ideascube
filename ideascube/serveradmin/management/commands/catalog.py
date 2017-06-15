import argparse

from django.core.management.base import CommandError

from ideascube.management.base import BaseCommandWithSubcommands
from ideascube.serveradmin.catalog import (Catalog,
                                           NoSuchPackage,
                                           ExistingRemoteError)


class Command(BaseCommandWithSubcommands):
    help = 'Manage apps and content'

    def add_arguments(self, parser):
        super().add_arguments(parser)

        required_ids = argparse.ArgumentParser('required_ids', add_help=False)
        required_ids.add_argument(
            'ids', nargs='+', metavar='ID',
            help='One or more package ids (or globs)')

        optional_ids = argparse.ArgumentParser('optional_ids', add_help=False)
        optional_ids.add_argument(
            'ids', nargs='*', metavar='ID', default=['*'],
            help='Optional package ids (or globs)')

        package_cache = argparse.ArgumentParser(
            'package_cache', add_help=False)
        package_cache.add_argument(
            '--package-cache', action='append', metavar='PATH', default=[],
            help='The path to an existing directory where downloaded packages'
                 ' can be found, in addition to the default package cache')
        package_cache.add_argument(
            '--keep-downloads', action='store_true',
            help='Keep the downloaded packages in the local cache after the '
                 'operation (the default is to discard them)')

        # -- Manage content ---------------------------------------------------
        list = self.subs.add_parser(
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
        group.add_argument(
            '--unhandled', action='store_const', dest='filter',
            const='unhandled',
            help='List unhandled packages.')
        list.set_defaults(filter='all', func=self.list_packages)

        install = self.subs.add_parser(
            'install', parents=[package_cache, required_ids],
            help='Install packages')
        install.set_defaults(func=self.install_packages)

        reinstall = self.subs.add_parser(
            'reinstall', parents=[package_cache, required_ids],
            help='Reinstall packages')
        reinstall.set_defaults(func=self.reinstall_packages)

        remove = self.subs.add_parser(
            'remove', parents=[required_ids], help='Remove packages')
        remove.set_defaults(func=self.remove_packages)

        upgrade = self.subs.add_parser(
            'upgrade', aliases=['update'],
            parents=[package_cache, optional_ids], help='Upgrade packages')
        upgrade.set_defaults(func=self.upgrade_packages)

        # -- Manage local cache -----------------------------------------------
        cache = self.subs.add_parser('cache', help='Manage cache')

        cachesubs = cache.add_subparsers(title='Commands', dest='cachecmd')
        cachesubs.required = True

        update = cachesubs.add_parser('update', help='Update the local cache')
        update.set_defaults(func=self.update_cache)

        clear = cachesubs.add_parser('clear', help='Clear the local cache')
        group = clear.add_mutually_exclusive_group()
        group.add_argument(
            '--metadata', action='store_const', dest='filter',
            const='metadata', help='Clear the cache of package metadata')
        group.add_argument(
            '--packages', action='store_const', dest='filter',
            const='packages', help='Clear the cache of downloaded packages')
        group.add_argument(
            '--all', action='store_const', dest='filter', const='all',
            help='Clear the whole cache (default)')
        clear.set_defaults(filter='all', func=self.clear_cache)

        # -- Manage remote sources --------------------------------------------
        remote = self.subs.add_parser('remotes', help='Manage remote sources')

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

    def handle(self, *args, **options):
        self.catalog = Catalog()

        return super().handle(*args, **options)

    # -- Manage content -------------------------------------------------------
    def list_packages(self, options):
        if not len(self.catalog.list_remotes()):
            print(
                "No remote sources configured, you won't see any available "
                "package.")
            print("Add a remote source with:\n")
            print("    {} remotes add ID NAME URL\n".format(self.parser.prog))

        fmt = (' {0.id:20}  {0.version!s:12}  {0.filesize:8}'
               ' {0.type:15} {0.name}')

        unhandled_pkgs = self.catalog.list_nothandled('*')
        if unhandled_pkgs:
            if options['filter'] == 'unhandled':
                print('Not handled packages')

                for pkg in unhandled_pkgs:
                    print(fmt.format(pkg))
            else:
                print(("Warning: Ignoring {} unsupported package(s)\n"
                       "Use '--unhandled' for details.\n\n"
                      ).format(len(unhandled_pkgs)))

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
        if options['package_cache'] is not None:
            for path in options['package_cache']:
                self.catalog.add_package_cache(path)

        try:
            self.catalog.install_packages(
                options['ids'], keep_downloads=options['keep_downloads'])

        except NoSuchPackage as e:
            raise CommandError('No such package: {}'.format(e))

    def remove_packages(self, options):
        self.catalog.remove_packages(options['ids'])

    def reinstall_packages(self, options):
        try:
            self.catalog.reinstall_packages(
                options['ids'], keep_downloads=options['keep_downloads'])

        except NoSuchPackage as e:
            raise CommandError('No such package: {}'.format(e))

    def upgrade_packages(self, options):
        if options['package_cache'] is not None:
            for path in options['package_cache']:
                self.catalog.add_package_cache(path)

        try:
            self.catalog.upgrade_packages(
                options['ids'], keep_downloads=options['keep_downloads'])

        except NoSuchPackage as e:
            raise CommandError('No such package: {}'.format(e))

    # -- Manage local cache ---------------------------------------------------
    def update_cache(self, options):
        self.catalog.update_cache()

    def clear_cache(self, options):
        if options['filter'] == 'metadata':
            self.catalog.clear_metadata_cache()

        elif options['filter'] == 'packages':
            self.catalog.clear_package_cache()

        else:
            self.catalog.clear_cache()

    # -- Manage remote sources ------------------------------------------------
    def list_remotes(self, options):
        for remote in self.catalog.list_remotes():
            print(remote)

    def add_remote(self, options):
        try:
            self.catalog.add_remote(options['id'], options['name'],
                                    options['url'])
        except ExistingRemoteError as e:
            if e.remote.url != options['url']:
                raise CommandError(
                    'There already is a "{0.id}" remote and urls differ '
                    '({0.url} and {1})'.format(e.remote, options['url']))
            print('Not adding already existing remote: "{}"'.format(options['id']))
        else:
            self.catalog.update_cache()

    def remove_remote(self, options):
        try:
            self.catalog.remove_remote(options['id'])
        except ValueError as e:
            raise CommandError(e)
        self.catalog.update_cache()
