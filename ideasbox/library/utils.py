import csv
import json
import os
import urllib
import urllib2

from django.core.files.base import ContentFile
from django.utils.translation import ugettext as _
from pymarc import MARCReader

OPENLIBRARY_API_URL = 'https://openlibrary.org/api/books?'


def to_unicode(text):
    """Do its best to return an unicode string."""
    if isinstance(text, unicode):
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
    args = {
        'jscmd': 'data',
        'format': 'json',
    }
    key = 'ISBN:{isbn}'.format(isbn=isbn)
    args['bibkeys'] = key
    query = urllib.urlencode(args)
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
        'title': data.get('title'),
        'authors': ', '.join([a['name'] for a in data.get('authors', [])]),
        'cover': cover,
        'publisher': publisher
    }
    return notice


def read_url(url):
    try:
        response = urllib2.urlopen(url)
        return response.read()
    except:
        # Catch all, we don't want to fail in any way.
        return None


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
        yield {
            'isbn': row['isbn'],
            # Moccam sucks in many ways, including encoding.
            'title': to_unicode(row['title']),
            'authors': to_unicode(authors),
            'publisher': to_unicode(row['publisher']),
            'summary': to_unicode(row['summary']),
            'cover': cover
        }


def load_unimarc(content):
    """Handle UNIMARC import.
    http://marc-must-die.info/index.php/Main_Page"""
    reader = MARCReader(content, to_unicode=True)
    for row in reader:
        if not row.title():
            continue
        yield {
            'isbn': row.isbn(),
            'title': row.title(),
            'authors': row.author() or '',
            'publisher': row.publisher() or '',
            'summary': '\n'.join([unicode(d)
                                  for d in row.physicaldescription()]),
        }
