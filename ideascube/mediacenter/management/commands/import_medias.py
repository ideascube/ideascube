# -*- coding: utf-8 -*-
import codecs
import csv
import mimetypes
import os
import sys

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from progressist import ProgressBar

from ideascube.mediacenter.models import Document
from ideascube.mediacenter.forms import DocumentForm
from ideascube.mediacenter.utils import guess_kind_from_content_type
from ideascube.templatetags.ideascube_tags import smart_truncate
from ideascube.management.utils import Reporter


class Bar(ProgressBar):
    template = 'Import: {percent} |{animation}| {done}/{total} | ETA: {eta}'


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

    def load(self, path):
        with codecs.open(path, 'r', encoding=self.encoding) as f:
            content = f.read()
            try:
                dialect = csv.Sniffer().sniff(content)
            except csv.Error:
                dialect = csv.unix_dialect()
            return csv.DictReader(content.splitlines(), dialect=dialect)

    def handle(self, *args, **options):
        path = os.path.abspath(options['path'])
        self.update = options['update']
        self.encoding = options['encoding']
        self.dry_run = options['dry_run']
        self.report = Reporter(options['verbosity'])
        if not os.path.exists(path):
            self.abort('Path does not exist: {}'.format(path))
        self.ROOT = os.path.dirname(path)
        rows = list(self.load(path))
        bar = Bar(total=sum(1 for i in rows))
        for row in bar.iter(rows):
            self.add(row)
        print(self.report)
        if self.report.has_errors():
            sys.exit(1)

    def add(self, metadata):
        title = metadata.get('title')
        if not title:
            self.report.error('Missing title', metadata)
            return
        title = smart_truncate(title)
        metadata['title'] = title

        if not metadata.get('lang'):
            metadata['lang'] = settings.LANGUAGE_CODE

        original = metadata.get('path')
        if not original:
            self.report.error('Missing path', metadata)
            return
        kind = metadata.get('kind')
        content_type, encoding = mimetypes.guess_type(original)
        if not kind or not hasattr(Document, kind.upper()):
            kind = guess_kind_from_content_type(content_type) or Document.OTHER
            metadata['kind'] = kind

        instance = Document.objects.filter(title=title, kind=kind).last()
        if instance and not self.update:
            self.report.warning('Document exists (Use --update for reimport)',
                                title)
            return

        path = os.path.join(self.ROOT, original)
        if not os.path.exists(path):
            self.report.error(u'Path not found', path)
            return
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
                self.report.notice('Metadata valid', metadata['title'])
            else:
                doc = form.save()
                self.report.notice('Uploaded media', str(doc))
        else:
            for field, error in form.errors.items():
                self.report.error('{}: {}'.format(field, error.as_text()),
                                  metadata)
