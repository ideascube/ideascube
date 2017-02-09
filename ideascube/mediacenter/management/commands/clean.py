# -*- coding: utf-8 -*-
import os
import argparse
import glob

from django.conf import settings
from django.core.management.base import BaseCommand

from ideascube.mediacenter.models import Document
from ideascube.utils import printerr


class Command(BaseCommand):
    help = 'Remove files from the mediacenter.'

    def add_arguments(self, parser):
        subs = parser.add_subparsers(
            title='Commands', dest='cmd', metavar='',
            parser_class=argparse.ArgumentParser)

        dry_run = argparse.ArgumentParser('dry_run', add_help=False)
        dry_run.add_argument('--dry-run', action='store_true',
                             help='Print the list of medias that would be '
                                  'removed. Do not actually remove them')

        clean_leftover = subs.add_parser(
            'leftover-files',
            parents = [dry_run],
            help='Clean mediacenter files not associated with a document.')
        clean_leftover.set_defaults(func=self.clean_leftover)

        clean_media = subs.add_parser(
            'media',
            parents = [dry_run],
            help='Remove all medias')
        clean_media.set_defaults(func=self.clean_media)

        self.parser = parser

    def handle(self, *args, **options):
        if 'func' not in options:
            self.parser.print_help()
            self.parser.exit(1)

        options['func'](options)

    def clean_media(self, options):
        Document.objects.filter(package_id='').delete()
        left_media_count = Document.objects.all().count()
        if left_media_count:
            print("{} media have been installed by packages."
                  " They have been not deleted.\n"
                  "You must delete the corresponding package if you want to "
                  "remove them. Use the command :\n"
                  "catalog remove pkgid+".format(left_media_count))
        self.clean_leftover(options)

    def clean_leftover(self, options):
        files_to_remove = self._get_leftover_files()
        if options['dry_run']:
            print("Files to remove are :")
            for _file in files_to_remove:
                print(" - '{}'".format(_file))
        else:
            for f in files_to_remove:
                try:
                    os.unlink(f)
                except Exception as e:
                    printerr("ERROR while deleting {}".format(f))
                    printerr("Exception is {}".format(e))

    def _get_leftover_files(self):
        # List all (original and preview) files in the fs
        original_files_root_dir = os.path.join(settings.MEDIA_ROOT,
                                               'mediacenter/document')
        files_in_fs = set(
            glob.iglob(os.path.join(original_files_root_dir, '*')))

        preview_files_root_dir = os.path.join(settings.MEDIA_ROOT,
                                    'mediacenter/preview')
        files_in_fs.update(
            glob.iglob(os.path.join(preview_files_root_dir, '*')))

        # Remove known original paths.
        original_pathes = Document.objects.all().values_list(
            'original', flat=True)
        original_pathes = (os.path.join(settings.MEDIA_ROOT, path)
                           for path in original_pathes)
        files_in_fs.difference_update(original_pathes)

        # Remove known preview paths.
        preview_pathes = Document.objects.all().values_list(
            'preview', flat=True)
        preview_pathes = (os.path.join(settings.MEDIA_ROOT, path)
                          for path in preview_pathes if path)
        files_in_fs.difference_update(preview_pathes)

        return files_in_fs
