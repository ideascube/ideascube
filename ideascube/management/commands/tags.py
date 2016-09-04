import argparse
import sys

from django.core.management.base import BaseCommand
from django.utils.termcolors import colorize

from taggit.models import Tag, TaggedItem


def log(text, **kwargs):
    sys.stdout.write(colorize(str(text), **kwargs) + '\n')


def notice(text, **kwargs):
    log(text, fg='blue')


def exit(text, **kwargs):
    log(text, fg='red')
    sys.exit(1)


class Command(BaseCommand):
    help = "Manage tags"

    def add_arguments(self, parser):
        self.parser = parser
        subs = parser.add_subparsers(
            title='Commands', dest='cmd', metavar='',
            parser_class=argparse.ArgumentParser)

        count = subs.add_parser('count', help='Count tag usage')
        count.add_argument('name', help='Tag name we want to count.')
        count.set_defaults(func=self.count)

        delete = subs.add_parser('delete', help='Delete tag')
        delete.add_argument('name', help='Tag name we want to delete.')
        delete.add_argument('--force', action='store_true',
                            help='Force delete even if tag is still used.')
        delete.set_defaults(func=self.delete)

        rename = subs.add_parser('rename', help='Rename a tag')
        rename.add_argument('old', help='Old name.')
        rename.add_argument('new', help='New name.')
        rename.set_defaults(func=self.rename)

        replace = subs.add_parser('replace',
                                  help='Replace tag by another and delete it')
        replace.add_argument('old', help='Old tag name.')
        replace.add_argument('new', help='New tag name.')
        replace.set_defaults(func=self.replace)

    def handle(self, *args, **options):
        if 'func' not in options:
            self.parser.print_help()
            self.parser.exit(1)

        log('-'*80, fg='white')
        options['func'](options)

    def _count(self, name):
        return TaggedItem.objects.filter(tag__name=name).count()

    def get_tag_or_exit(self, name):
        tag = Tag.objects.filter(name=name).first()
        if not tag:
            exit('No tag found with name "{}"'.format(name))
        return tag

    def count(self, options):
        count = self._count(options['name'])
        notice('{count} object(s) tagged with "{name}"'.format(count=count,
                                                               **options))

    def delete(self, options):
        name = options['name']
        tag = self.get_tag_or_exit(name)
        count = self._count(name)
        force = options.get('force')
        if count and not force:
            confirm = input('Tag "{}" is still linked to {} items.\n'
                            'Type "yes" to confirm delete or "no" to '
                            'cancel: '.format(name, count))
            if confirm != 'yes':
                exit("Delete cancelled.")
        tag.delete()
        notice('Deleted tag "{name}".'.format(**options))

    def rename(self, options):
        if options['old'] == options['new']:
            exit('Nothing to rename, tags are equal.')
        tag = self.get_tag_or_exit(options['old'])
        if Tag.objects.filter(name=options['new']).exclude(pk=tag.pk).exists():
            exit('Tag "{new}" already exists. Aborting.'.format(**options))
        tag.name = options['new']
        tag.save()
        notice('Renamed "{old}" to "{new}".'.format(**options))

    def replace(self, options):
        if options['old'] == options['new']:
            exit('Nothing to rename, tags are equal.')
        old = self.get_tag_or_exit(options['old'])
        new, created = Tag.objects.get_or_create(name=options['new'])
        if created:
            notice('Created tag "{new}"'.format(**options))
        relations = TaggedItem.objects.filter(tag=old)
        for relation in relations:
            content = relation.content_object
            notice('Processing "{}"'.format(repr(content)))
            relation.delete()
            content.tags.add(new)
        old.delete()
        notice('Deleted "{}"'.format(old))
