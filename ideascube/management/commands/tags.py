import argparse
import sys
from itertools import groupby
from operator import itemgetter

from django.core.management.base import BaseCommand
from django.utils.termcolors import colorize

from taggit.models import Tag, TaggedItem
from ideascube.utils import sanitize_tag_name


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

        sanitize = subs.add_parser('sanitize',
            help=('Sanitize existing tags.\n'
                  'Remove duplicates, clean characters...'))
        sanitize.set_defaults(func=self.sanitize)

        list_ = subs.add_parser('list', help='List tags')
        list_.set_defaults(func=self.list)

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

    def list(self, options):
        row = '{:<40}{:<40}{}'
        print(row.format('name', 'slug', 'count'))
        print(row.format('.' * 40, '.' * 40, '.' * 40))
        for tag in Tag.objects.order_by('slug'):
            print(row.format(tag.name, tag.slug, self._count(tag.name)))

    def sanitize(self, options):
        all_tags = ((sanitize_tag_name(t.name), t) for t in Tag.objects.all())
        all_tags = sorted(all_tags, key=itemgetter(0))
        all_tags = groupby(all_tags, key=itemgetter(0))
        for new_tag_name, tags in all_tags:
            tags = (t[1] for t in tags)
            if not new_tag_name:
                # No need to delete relation, happy cascading !
                for tag in tags:
                    tag.delete()
                continue

            tag = next(tags)
            other_equivalent_tags = list(tags)

            # All the relations we need to redirect to `tag`
            other_relations = TaggedItem.objects.filter(
                tag__in=other_equivalent_tags)
            for relation in other_relations:
                # if an object `o` is tagged with tag `foo` and `Foo`, the
                # relation `o-Foo` must be change to `o-foo`. But this relation
                # already exists, so, instead, we must delete `o-Foo`,
                # not change it.
                existing_relations = TaggedItem.objects.filter(
                        tag=tag,
                        object_id=relation.content_object.id,
                        content_type = relation.content_type)
                if not existing_relations.exists():
                    # We must change the relation
                    relation.tag = tag
                    relation.save()
                else:
                    # We have existing relation(s).
                    # We should not have more than one because we cannot have
                    # the *exact* same relation twice but let's be safe :
                    # delete any extra relation.
                    extra_relations = list(existing_relations)[1:]
                    for rel in extra_relations:
                        rel.delete()
                    # Then delete the current relation because we know we have
                    # an existing relation.
                    relation.delete()

            # There is no relation to other tags left, delete them.
            for t in other_equivalent_tags:
                t.delete()

            # Be sure our tag is correctly renamed.
            # We do it at the end because the tag's name is unique and so,
            # we want to be sure that all potential duplicates have been
            # deleted/changed.
            tag.name = new_tag_name
            tag.save()
