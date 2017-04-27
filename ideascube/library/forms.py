import csv
import re
import zipfile

from django import forms
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils.translation import get_language, ugettext_lazy as _

from ideascube.utils import TextIOWrapper
from ideascube.widgets import LangSelect

from .models import Book, BookSpecimen
from .utils import (fetch_from_openlibrary, load_from_ideascube,
                    load_from_moccam_csv, load_unimarc)


class BookSpecimenForm(forms.ModelForm):

    def clean_barcode(self):
        barcode = self.cleaned_data['barcode']

        # Keep only letters
        barcode = re.sub(r'\s', '', barcode)

        # Make sure empty values are mapped to None, not empty strings (we need
        # NULL values in db, not empty strings, for uniqueness constraints).
        return barcode or None

    def clean_file(self):
        # Ensure specimenfile and barcode are not both filled or both set to
        # None.
        if all([self.cleaned_data['file'], self.cleaned_data['barcode']]):
            raise ValidationError(_("You can't have both a file and a barcode"))
        if not any([self.cleaned_data['file'], self.cleaned_data['barcode']]):
            raise ValidationError(_("You must add a file or a barcode"))
        return self.cleaned_data['file']

    class Meta:
        model = BookSpecimen
        widgets = {'item': forms.HiddenInput}
        exclude = ['serial', 'count']


class BookSpecimenImportForm(forms.Form):
    source = forms.FileField(label=_('CSV File'), required=True)

    def clean_source(self):
        if not zipfile.is_zipfile(self.cleaned_data['source']):
            raise ValidationError(_('Uploaded file is not a Zip archive'))

        with zipfile.ZipFile(self.cleaned_data['source'].file) as zip:
            for name in zip.namelist():
                if name.endswith('.csv'):
                    self.cleaned_data['csvfilename'] = name
                    break

            else:
                raise ValidationError(_('Archive does not contain a CSV'))

        return self.cleaned_data['source']

    def save(self):
        source = self.cleaned_data['source'].file
        csvfilename = self.cleaned_data['csvfilename']
        items = []
        errors = []

        with zipfile.ZipFile(source) as zip:
            with TextIOWrapper(zip.open(csvfilename, mode='r')) as csvfile:
                for index, row in enumerate(csv.DictReader(csvfile)):
                    linenum = index + 2  # Start at 0 and first header line

                    try:
                        data = {
                            'barcode': row['barcode'],
                            'comments': row['comments'],
                            'location': row['location'],
                            'serial': row['serial'],
                            'file': row['file'],
                            'isbn': row['isbn'],
                            'title': row['title'],
                        }

                    except KeyError as e:
                        errors.append(_(
                            'Missing column "{}" on line {}').format(
                                e.args[0], linenum))
                        continue

                    # Get the related book item
                    isbn = data.pop('isbn')
                    title = data.pop('title')

                    if isbn:
                        try:
                            data['item'] = Book.objects.get(isbn=isbn).pk

                        except Book.DoesNotExist:
                            errors.append(
                                _('Could not import line {}: no book with ISBN'
                                ' "{}"').format(linenum, isbn))
                            continue

                    else:
                        try:
                            data['item'] = Book.objects.get(name=title).pk

                        except Book.DoesNotExist:
                            errors.append(_(
                                'Could not import line {}: no "{}" book'
                                ).format(linenum, title))
                            continue

                        except Book.MultipleObjectsReturned:
                            errors.append(_(
                                'Could not import line {}: found multiple '
                                '"{}" books').format(linenum, title))
                            continue

                    # Get the file if the specimen is digital
                    filename = data.pop('file')
                    files = {}

                    if filename:
                        try:
                            files['file'] = ContentFile(
                                zip.open(filename).read(), name=filename)

                        except KeyError:
                            errors.append(_(
                                'Could not import line {}: file {} is missing '
                                'from the archive').format(
                                    linenum, filename))
                            continue

                    form = BookSpecimenForm(data=data, files=files)

                    if form.is_valid():
                        item = form.save()
                        items.append(item)

                    else:
                        msgs = (
                            '{}: {}'.format(k, v.as_text())
                            for k, v in form.errors.items())
                        errors.append(_('Could not import line {}: {}').format(
                            linenum, '; '.join(msgs)))
                        continue

        return items, errors[:10]


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        exclude = ['module']
        labels = {
            'name': _('title'),
        }
        widgets = {
            'lang': LangSelect
        }

    def clean_isbn(self):
        isbn = self.cleaned_data['isbn']

        # Keep only integers
        isbn = re.sub(r'\D', '', isbn)

        # Make sure empty values are mapped to None, not empty strings (we need
        # NULL values in db, not empty strings, for uniqueness constraints).
        return isbn or None

    def save(self, commit=True):
        book = super().save()
        book.save()  # Index m2m.
        return book


class ImportForm(forms.Form):

    MOCCAM_CSV = 'moccam_csv'
    UNIMARC = 'unimarc'
    IDEASCUBE = 'ideascube'
    FORMATS = (
        (MOCCAM_CSV, _('CSV from "MoCCam-en-ligne"')),
        (UNIMARC, 'UNIMARC'),
        (IDEASCUBE, _('Ideascube ZIP')),
    )

    from_files = forms.FileField(required=False)
    files_format = forms.ChoiceField(choices=FORMATS)
    from_isbn = forms.CharField(widget=forms.Textarea, required=False)

    def save_from_files(self):
        """Create or update books from given metadata files."""
        files = self.cleaned_data['from_files']
        format_ = self.cleaned_data['files_format']
        if format_ == self.MOCCAM_CSV:
            handler = load_from_moccam_csv
        elif format_ == self.UNIMARC:
            handler = load_unimarc
        elif format_ == self.IDEASCUBE:
            handler = load_from_ideascube
        else:
            raise ValueError(_('Unknown file format'))
        books = []
        for notice, cover in handler(files):
            if not notice:
                continue
            notice.setdefault('section', Book.OTHER)
            notice.setdefault('lang', get_language())
            isbn = notice.get('isbn')
            instance = None
            if isbn:
                instance = Book.objects.filter(isbn=isbn).first()
            form = BookForm(data=notice, files={'cover': cover},
                            instance=instance)
            if form.is_valid():
                book = form.save()
                books.append(book)
        return books

    def save_from_isbn(self):
        """Create or update books from given ISBN, using OpenLibrary API."""
        isbns = self.cleaned_data['from_isbn'].splitlines()
        books = []
        for isbn in isbns:
            notice = fetch_from_openlibrary(isbn)
            if not notice:
                continue
            notice['section'] = Book.OTHER
            book, _ = Book.objects.update_or_create(isbn=notice['isbn'],
                                                    defaults=notice)
            books.append(book)
        return books
