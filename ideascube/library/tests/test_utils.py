# -*- coding: utf-8 -*-
import pytest

from ..utils import (fetch_from_openlibrary, load_from_moccam_csv,
                     load_unimarc, to_unicode)


def test_load_from_moccam_csv(monkeypatch):
    monkeypatch.setattr('ideascube.library.utils.load_cover_from_url',
                        lambda x: 'xxx')
    with open('ideascube/library/tests/data/moccam.csv') as f:
        notices = list(load_from_moccam_csv(f.read()))
        assert len(notices) == 2
        notice, cover = notices[0]
        assert notice['name'] == 'Les Enchanteurs'
        assert notice['authors'] == 'Romain Gary'
        assert notice['publisher'] == 'Gallimard'
        assert notice['description'].startswith('Le narrateur')
        assert cover == 'xxx'


def test_load_unimarc(monkeypatch):
    with open('ideascube/library/tests/data/marc.dat') as f:
        notices = [notice for notice, cover in load_unimarc(f.read())]
        assert len(notices) == 20
        assert notices[0]['name'] == 'The pragmatic programmer : from journeyman to master /'  # noqa
        assert notices[0]['authors'] == 'Hunt, Andrew, 1964-'
        assert notices[0]['publisher'] == 'Addison-Wesley,'


def test_fetch_from_openlibrary(monkeypatch):
    doc = b"""{"ISBN:2070379043": {"publishers": [{"name": "Gallimard"}], "identifiers": {"isbn_13": ["9782070379040"], "openlibrary": ["OL8838456M"], "isbn_10": ["2070379043"], "goodreads": ["118988"], "librarything": ["1655982"]}, "weight": "7 ounces", "title": "Les Enchanteurs", "url": "https://openlibrary.org/books/OL8838456M/Les_enchanteurs", "number_of_pages": 373, "cover": {"small": "https://covers.openlibrary.org/b/id/967767-S.jpg", "large": "https://covers.openlibrary.org/b/id/967767-L.jpg", "medium": "https://covers.openlibrary.org/b/id/967767-M.jpg"}, "publish_date": "January 22, 1988", "key": "/books/OL8838456M", "authors": [{"url": "https://openlibrary.org/authors/OL123692A/Romain_Gary", "name": "Romain Gary"}]}}"""  # noqa
    monkeypatch.setattr('ideascube.library.utils.load_cover_from_url',
                        lambda x: 'xxx')
    monkeypatch.setattr('ideascube.library.utils.read_url', lambda x: doc)
    notice = fetch_from_openlibrary('2070379043')
    assert notice['name'] == 'Les Enchanteurs'
    assert notice['authors'] == 'Romain Gary'
    assert notice['cover'] == 'xxx'
    assert notice['publisher'] == 'Gallimard'


@pytest.mark.parametrize('string', [
    u'éééé'.encode('latin-1'),
    u'éééé'
])
def test_to_unicode(string):
    assert isinstance(to_unicode(string), str)
