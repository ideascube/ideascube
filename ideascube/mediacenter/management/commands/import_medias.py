# -*- coding: utf-8 -*-
import csv
import mimetypes
import os
import sys

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand

from ideascube.mediacenter.models import Document
from ideascube.mediacenter.forms import DocumentForm
from ideascube.mediacenter.utils import guess_kind_from_content_type


class Command(BaseCommand):
    help = ('Batch import medias from CSV metadata. CSV file must contain '
            'columns "title", "summary", "path", "credits". Optional columns '
            'are "lang", "preview", "kind", "tags".')

    def add_arguments(self, parser):
        parser.add_argument('path', help='Path to CSV metadata.')
        parser.add_argument('--update', action='store_true', default=False,
                            help='Update instance when document with same '
                                 'title and kind is found in db.')

    def abort(self, msg):
        self.stderr.write(msg)
        sys.exit(1)

    def skip(self, msg, metadata):
            self.stderr.write(u'⚠ Skipping. {}.'.format(msg.decode('utf-8')))
            for key, value in metadata.items():
                value = value.decode('utf-8') if value else ''
                self.stdout.write(u'- {}: {}'.format(key, value))
            self.stdout.write('-' * 20)

    def load(self, path):
        with open(path, 'r') as f:
            extract = f.read(4096)
            try:
                dialect = csv.Sniffer().sniff(extract)
            except csv.Error:
                dialect = csv.unix_dialect()
            f.seek(0)
            content = f.read()
            return csv.DictReader(content.splitlines(),
                                  dialect=dialect)

    def handle(self, *args, **options):
        path = os.path.abspath(options['path'])
        self.update = options['update']
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
            return self.skip('Document exists. Use --update to reimport data',
                             metadata)

        path = os.path.join(self.ROOT, original)
        if not os.path.exists(path):
            return self.skip('Path not found: {}'.format(path), metadata)
        with open(path, 'rb') as f:
            original = SimpleUploadedFile(original, f.read(),
                                          content_type=content_type)

        preview = metadata.get('preview')
        if preview:
            path = os.path.join(self.ROOT, preview)
            with open(path, 'rb') as f:
                preview = SimpleUploadedFile(preview, f.read())

        files = dict(original=original, preview=preview)
        form = DocumentForm(data=metadata, files=files, instance=instance)

        if form.is_valid():
            doc = form.save()
            self.stdout.write(u'✔ Uploaded media {}'.format(doc))
        else:
            for field, error in form.errors.items():
                self.skip('{}: {}'.format(field, error.as_text()), metadata)
