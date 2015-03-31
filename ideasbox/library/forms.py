import re

from django import forms

from .models import Book, BookSpecimen, BookSpecimenDigital
from .utils import fetch_from_openlibrary, load_from_moccam_csv, load_unimarc


class BookSpecimenForm(forms.ModelForm):

    class Meta:
        model = BookSpecimen
        widgets = {'book': forms.HiddenInput}
        fields = '__all__'

class BookSpecimenDigitalForm(forms.ModelForm):
#
    class Meta:
        model = BookSpecimenDigital
        widgets = {'book': forms.HiddenInput}
        fields = ['book','remarks']

class BookForm(forms.ModelForm):

    def clean_isbn(self):
        # Keep only integers, and make sure empty values are mapped to None,
        # not empty string (we need NULL values in db, not empty strings, for
        # uniqueness constraints).
        return re.sub(r'\D', '', self.cleaned_data['isbn']) or None

    class Meta:
        model = Book
        fields = '__all__'


class ImportForm(forms.Form):

    MOCCAM_CSV = 'moccam_csv'
    UNIMARC = 'unimarc'
    FORMATS = (
        (MOCCAM_CSV, 'CSV from "Mocam-en-ligne"'),
        (UNIMARC, 'UNIMARC'),
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
        books = []
        for f in files:
            for notice in handler(f):
                notice['section'] = Book.OTHER
                book, _ = Book.objects.update_or_create(isbn=notice['isbn'],
                                                        defaults=notice)
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
