import argparse

from django.core.management.base import BaseCommand

from ideascube.configuration.registry import (
    get_all_namespaces,
    )


class Command(BaseCommand):
    help = 'Manage server configuration'

    def add_arguments(self, parser):
        subs = parser.add_subparsers(
            title='Commands', dest='cmd', metavar='',
            parser_class=argparse.ArgumentParser)

        list = subs.add_parser(
            'list', help='List configuration namespaces and keys')
        list.set_defaults(func=self.list_configs)

        self.parser = parser

    def handle(self, *_, **options):
        if 'func' not in options:
            self.parser.print_help()
            self.parser.exit(1)

        options['func'](options)

    def list_configs(self, options):
        for namespace in get_all_namespaces():
            print(namespace)
