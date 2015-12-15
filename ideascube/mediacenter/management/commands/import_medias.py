# -*- coding: utf-8 -*-
import csv
import mimetypes
import os
import sys

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from ideascube.mediacenter.models import Document
from ideascube.mediacenter.forms import DocumentForm
from ideascube.mediacenter.utils import guess_kind_from_content_type
from ideascube.templatetags.ideascube_tags import smart_truncate


def UnicodeDictReader(utf8_data, encoding='utf-8', **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        print(row)
        yield {key.decode(encoding): value.decode(encoding)
               for key, value in row.iteritems()}


class Command(BaseCommand):
    help = ('Batch import medias from CSV metadata. CSV file must contain '
            'columns "title", "summary", "path", "credits". Optional columns '
            'are "lang", "preview", "kind", "tags".')

    def add_arguments(self, parser):
        parser.add_argument('path', help='Path to CSV metadata.')
        parser.add_argument('--update', action='store_true', default=False,
                            help='Update instance when document with same '
                                 'title and kind is found in db.')
        parser.add_argument('--encoding', default='utf-8',
                            help='Define csv encoding.')
        parser.add_argument('--dry-run', action='store_true',
                            help='Only check data, do not save.')

    def abort(self, msg):
        self.stderr.write(msg)
        sys.exit(1)

    def skip(self, msg, metadata=None):
        self.stderr.write(u'⚠ Skipping. {}.'.format(msg))
        if metadata:
            for key, value in metadata.items():
                value = value if value else ''
                self.stdout.write(u'- {}: {}'.format(key, value))
        self.stdout.write('-' * 20)

    def load(self, path):
        with open(path, 'r') as f:
            extract = f.read()
            try:
                dialect = csv.Sniffer().sniff(extract)
            except csv.Error:
                dialect = csv.unix_dialect()
            f.seek(0)
            content = f.read()
            return UnicodeDictReader(content.splitlines(),
                                     encoding=self.encoding,
                                     dialect=dialect)

    def handle(self, *args, **options):
        path = os.path.abspath(options['path'])
        self.update = options['update']
        self.encoding = options['encoding']
        self.dry_run = options['dry_run']
        if not os.path.exists(path):
            self.abort('Path does not exist: {}'.format(path))
        self.ROOT = os.path.dirname(path)
        rows = self.load(path)
        for row in rows:
            self.add(row)

    def add(self, metadata):
        title = metadata.get('title')
        if not title:
            return self.skip('Missing title', metadata)
        title = smart_truncate(title)
        metadata['title'] = title

        if not metadata.get('lang'):
            metadata['lang'] = settings.LANGUAGE_CODE

        original = metadata.get('path')
        if not original:
            return self.skip('Missing path', metadata)
        kind = metadata.get('kind')
        content_type, encoding = mimetypes.guess_type(original)
        if not kind or not hasattr(Document, kind.upper()):
            kind = guess_kind_from_content_type(content_type) or Document.OTHER
            metadata['kind'] = kind

        instance = Document.objects.filter(title=title, kind=kind).last()
        if instance and not self.update:
            return self.skip(u'Document "{}" exists. Use --update to reimport '
                             u'data'.format(title))

        path = os.path.join(self.ROOT, original)
        if not os.path.exists(path):
            return self.skip(u'Path not found: {}'.format(path),
                             metadata)
        with open(path, 'rb') as f:
            original = File(f, name=original)

            preview = metadata.get('preview')
            if preview:
                path = os.path.join(self.ROOT, preview)
                with open(path, 'rb') as f:
                    preview = File(f, name=preview)
                    self.save(metadata, original, instance, preview)
            else:
                self.save(metadata, original, instance)

    def save(self, metadata, original, instance, preview=None):
        files = dict(original=original, preview=preview)
        form = DocumentForm(data=metadata, files=files, instance=instance)

        if form.is_valid():
            if self.dry_run:
                self.stdout.write(u'✔ Metadata valid {}'.format(
                                                            metadata['title']))
            else:
                doc = form.save()
                self.stdout.write(u'✔ Uploaded media {}'.format(doc))
        else:
            for field, error in form.errors.items():
                self.skip('{}: {}'.format(field, error.as_text()), metadata)
