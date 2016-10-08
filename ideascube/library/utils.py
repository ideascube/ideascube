import csv
import json
import os
from urllib.parse import urlencode
from urllib.request import urlopen
import zipfile

from django.core.files.base import ContentFile
from django.utils.translation import ugettext as _
from pymarc import MARCReader

OPENLIBRARY_API_URL = 'https://openlibrary.org/api/books?'


def to_unicode(text):
    """Do its best to return an unicode string."""
    text = text or ''
    if isinstance(text, str):
        return text
    else:
        try:
            text = text.decode('utf-8')
        except UnicodeDecodeError:
            text = text.decode('latin-1')
        return text


def fetch_from_openlibrary(isbn):
    """Fetch notice from Open Library and return a ready to use dict.
    Doc: https://openlibrary.org/dev/docs/api/books."""
    isbn = isbn.strip()
    args = {
        'jscmd': 'data',
        'format': 'json',
    }
    key = 'ISBN:{isbn}'.format(isbn=isbn)
    args['bibkeys'] = key
    query = urlencode(args)
    url = '{base}{query}'.format(base=OPENLIBRARY_API_URL, query=query)
    content = read_url(url)
    try:
        data = json.loads(content).get(key)
    except ValueError:
        return
    if not data:
        return
    url = data.get('cover', {}).get('medium')
    if url:
        cover = load_cover_from_url(url)
    else:
        cover = None
    publishers = data.get('publishers', [])
    if publishers:
        publisher = publishers[0]['name']
    else:
        publisher = None
    notice = {
        'isbn': isbn,
        'name': data.get('title'),
        'authors': ', '.join([a['name'] for a in data.get('authors', [])]),
        'cover': cover,
        'publisher': publisher
    }
    return notice


def read_url(url):
    try:
        response = urlopen(url)
        return response.read().decode()
    except:
        # Catch all, we don't want to fail in any way.
        return ''


def load_cover_from_url(url):
    content = read_url(url)
    name = os.path.basename(url)
    if content and name:
        return ContentFile(content, name=name)


def load_from_moccam_csv(content):
    """Handle Moccam CSV import.
    See http://www.moccam-en-ligne.fr
    """
    FIELDS = [
        'isbn', 'title', 'authors', 'publisher', 'collection', 'year', 'price',
        'summary', 'small_cover', 'cover'
    ]
    if hasattr(content, 'read'):
        content = content.read().decode()
    content = content.split('\n')
    rows = csv.DictReader(content, fieldnames=FIELDS, delimiter='\t')
    if rows.restkey or rows.restval:
        raise ValueError(_('Badly formatted file'))
    for row in rows:
        if row['cover']:
            cover = load_cover_from_url(row['cover'])
        else:
            cover = None
        authors = row.get('authors', '')
        if ',' in authors:
            authors = authors.split(', ')
            authors.reverse()  # They are in the form "Gary, Romain".
            authors = ' '.join(authors)
        notice = {
            'isbn': row['isbn'],
            # Moccam sucks in many ways, including encoding.
            'name': to_unicode(row['title']),
            'authors': to_unicode(authors),
            'publisher': to_unicode(row['publisher']),
            'description': to_unicode(row['summary'])
        }
        yield notice, cover


def load_unimarc(content):
    """Handle UNIMARC import.
    http://marc-must-die.info/index.php/Main_Page"""
    if hasattr(content, 'read'):
        content = content.read().decode()
    reader = MARCReader(content.encode(), to_unicode=True)
    for row in reader:
        if not row.title():
            continue
        notice = {
            'isbn': row.isbn(),
            'name': row.title(),
            'authors': row.author() or '',
            'publisher': row.publisher() or '',
            'description': '\n'.join(
                [str(d) for d in row.physicaldescription()]),
        }
        yield notice, None


def load_from_zip(zip, name):
    return zip.open(name).read()


def load_from_ideascube(content):
    assert zipfile.is_zipfile(content), _('Not a zip file')
    archive = zipfile.ZipFile(content)
    csv_filename = None
    for name in archive.namelist():
        if name.endswith('.csv'):
            csv_filename = name
            break
    assert csv_filename, _('Missing CSV file in zip')
    csv_content = load_from_zip(archive, csv_filename).decode()
    rows = csv.DictReader(csv_content.splitlines())
    for row in rows:
        cover_filename = row.get('cover')
        if cover_filename:
            cover = ContentFile(load_from_zip(archive, cover_filename),
                                name=cover_filename)
        else:
            cover = None
        notice = {
            'isbn': row.get('isbn'),
            'authors': to_unicode(row.get('authors')),
            'serie': to_unicode(row.get('serie')),
            'name': to_unicode(row.get('name')),
            'subtitle': to_unicode(row.get('subtitle')),
            'description': to_unicode(row.get('description')),
            'publisher': to_unicode(row.get('publisher')),
            'section': to_unicode(row.get('section')),
            'lang': to_unicode(row.get('lang')),
            'tags': to_unicode(row.get('tags')),
        }
        yield notice, cover
