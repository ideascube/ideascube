import argparse

from django.core.management.base import BaseCommand as DjangoBaseCommand


class BaseCommandWithSubcommands(DjangoBaseCommand):
    def add_arguments(self, parser):
        self.parser = parser
        self.subs = parser.add_subparsers(
            title='Commands', dest='cmd', metavar='',
            parser_class=argparse.ArgumentParser)

    def handle(self, *args, **options):
        if 'func' not in options:
            self.parser.print_help()
            self.parser.exit(1)

        options['func'](options)
