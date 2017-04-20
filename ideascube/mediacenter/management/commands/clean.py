# -*- coding: utf-8 -*-
import os
import argparse
from pathlib import Path

from django.conf import settings

from ideascube.management.base import BaseCommandWithSubcommands
from ideascube.management.args import date_argument
from ideascube.mediacenter.models import Document
from ideascube.utils import printerr


class Command(BaseCommandWithSubcommands):
    help = 'Remove files from the mediacenter.'

    def add_arguments(self, parser):
        super().add_arguments(parser)

        dry_run = argparse.ArgumentParser('dry_run', add_help=False)
        dry_run.add_argument('--dry-run', action='store_true',
                             help='Print the list of medias that would be '
                                  'removed. Do not actually remove them')

        clean_leftover = self.subs.add_parser(
            'leftover-files',
            parents = [dry_run],
            help='Clean mediacenter files not associated with a document.')
        clean_leftover.set_defaults(func=self.clean_leftover)

        document_types = [choice[0] for choice in Document.KIND_CHOICES]

        clean_media = self.subs.add_parser(
            'media',
            parents = [dry_run],
            help='Remove all medias')
        clean_media.add_argument(
            '--type', action='append', choices=document_types,
            help='The type of media to remove, e.g "--types=image". Can be '
                 'specified multiple times to clean multiple types.')
        clean_media.add_argument(
            '--created-after', type=date_argument,
            help='Only remove media created on or after this date.')
        clean_media.add_argument(
            '--created-before', type=date_argument,
            help='Only remove media created before this date.')
        clean_media.set_defaults(func=self.clean_media)

    def _get_filtered_queryset(self, queryset, options):
        type_ = options['type']
        created_after = options['created_after']
        created_before = options['created_before']

        if type_:
            queryset = queryset.filter(kind__in=type_)

        if created_after:
            queryset = queryset.filter(created_at__gte=created_after)

        if created_before:
            queryset = queryset.filter(created_at__lt=created_before)

        return queryset

    def clean_media(self, options):
        documents = Document.objects.filter(package_id='')
        documents = self._get_filtered_queryset(documents, options)
        documents_count = documents.count()

        from_packages = Document.objects.exclude(package_id='')
        from_packages = self._get_filtered_queryset(from_packages, options)
        from_packages_count = from_packages.count()

        if not options['dry_run']:
            documents.delete()
            self.stdout.write(
                '{} documents have been deleted.'.format(documents_count))
            have_not = 'have not been'

        else:
            self.stdout.write(
                '{} documents would have been deleted:'.format(
                    documents_count))

            for document in documents:
                self.stdout.write('- {0.title} ({0.kind})'.format(document))

            have_not = 'would not have been'

        if from_packages_count:
            self.stdout.write(
                "\n{} media have been installed by packages and {} deleted.\n"
                "Remove the corresponding package(s) if you want to delete "
                "them with the command:\n"
                "catalog remove pkgid+".format(from_packages_count, have_not))

        if not options['dry_run']:
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
                    f.unlink()
                except Exception as e:
                    printerr("ERROR while deleting {}".format(f))
                    printerr("Exception is {}".format(e))

    def _get_leftover_files(self):
        # List all (original and preview) files in the fs
        original_files_root_dir = os.path.join(settings.MEDIA_ROOT,
                                               'mediacenter/document')
        files_in_fs = set(
            Path(original_files_root_dir).glob('**/*'))

        preview_files_root_dir = os.path.join(settings.MEDIA_ROOT,
                                    'mediacenter/preview')
        files_in_fs.update(
            Path(preview_files_root_dir).glob('**/*'))

        files_in_fs = {p for p in files_in_fs if not p.is_dir()}

        # Remove known original paths.
        original_pathes = Document.objects.all().values_list(
            'original', flat=True)
        original_pathes = (Path(settings.MEDIA_ROOT, path)
                           for path in original_pathes)
        files_in_fs.difference_update(original_pathes)

        # Remove known preview paths.
        preview_pathes = Document.objects.all().values_list(
            'preview', flat=True)
        preview_pathes = (Path(settings.MEDIA_ROOT, path)
                          for path in preview_pathes if path)
        files_in_fs.difference_update(preview_pathes)

        return files_in_fs
