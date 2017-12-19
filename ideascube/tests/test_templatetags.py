# -*- coding: utf-8 -*-
import pytest

from django.http import QueryDict

from ideascube.blog.tests.factories import ContentFactory
from ideascube.library.tests.factories import BookFactory
from ideascube.mediacenter.models import Document
from ideascube.mediacenter.tests.factories import DocumentFactory

from ..templatetags.ideascube_tags import (do_min, fa, remove_i18n,
                                           smart_truncate, theme_slug,
                                           _is_in_qs,  _add_qs, _replace_qs,
                                           _remove_qs)

pytestmark = pytest.mark.django_db


def test_theme_slug_for_content():
    content = ContentFactory()
    assert theme_slug(content) == '<span class="theme create">blog</span>'


def test_theme_slug_for_book():
    book = BookFactory()
    assert theme_slug(book) == '<span class="theme read">book</span>'


def test_theme_slug_for_document():
    book = DocumentFactory(kind=Document.IMAGE)
    assert theme_slug(book) == '<span class="theme discover">image</span>'


def test_theme_slug_can_be_overrided():
    book = BookFactory()
    assert theme_slug(book, "xxx") == '<span class="theme read">xxx</span>'


@pytest.mark.parametrize('given,expected', [
    ['/', '/'],
    ['/en/xxxx/', '/xxxx/'],
])
def test_remove_i18n(given, expected):
    assert remove_i18n(given) == expected


def test_fa_without_extra():
    assert fa('pencil') == '<span class="fa fa-pencil"></span>'


def test_fa_with_extra():
    assert fa('pencil', 'fa-fw') == '<span class="fa fa-pencil fa-fw"></span>'


@pytest.mark.parametrize('left,right,expected', [
    [0, 100, 0],
    [27, 22, 22],
])
def test_do_min(left, right, expected):
    assert do_min(left, right) == expected
    assert do_min(right, left) == expected


@pytest.mark.parametrize('given,expected,length,suffix', [
    [u'Ceci est une longue phrase qui pourrait éventuellement servir de titre à billet de blog mais est vraiment beaucoup trop longue',  # noqa
     u'Ceci est une longue phrase qui pourrait éventuellement servir de titre à billet de blog mais est…', None, None],  # noqa
    ['A short sentence', 'A short sentence', None, None],
    ['A short sentence', u'A short…', 10, None],
    ['A short sentence', u'A short.', 10, '.'],
    ['A short sentence', u'A short', 10, ''],
    [u"أكثر من خمسين لغة،", u"أكثر من خمسين لغة،", None, None],
    [u"أكثر من خمسين لغة،", u"أكثر…", 5, None],
    ["I'm 17 chars long", "I'm 17 chars long", 17, None],
    ["I've a space at 13", u"I've a space…", 13, None],
    ["I've a space at 13", u"I've a space…", 14, None],
    ["I've a space at 13", u"I've a…", 12, None],
    ['Anticonstitutionnellement', u'Anticon…', 8, None],
    ["I've a comma, at 13", u"I've a comma…", 14, None],
    ["", u"", None, None],
])
def test_smart_struncate(given, expected, length, suffix):
    kwargs = {}
    if length is not None:
        kwargs['length'] = length
    if suffix is not None:
        kwargs['suffix'] = suffix
    assert smart_truncate(given, **kwargs) == expected


def test_is_in_qs_empty():
    assert _is_in_qs(QueryDict(), 'foo', 'bar') == False


def test_is_in_qs_is_in():
    query = QueryDict(mutable=True)
    query.update({'foo': 'bar'})
    assert _is_in_qs(query, 'foo', 'bar') == True


def test_is_in_qs_wrong_value():
    query = QueryDict(mutable=True)
    query.update({'foo': 'bar'})
    assert _is_in_qs(query, 'foo', 'baz') == False


def test_is_in_qs_wrong_key():
    query = QueryDict(mutable=True)
    query.update({'foo': 'bar'})
    assert _is_in_qs(query, 'key', 'bar') == False


def test_add_qs_to_empty():
    params = _add_qs(QueryDict(mutable=True), foo='bar', bar='foo')
    assert dict(params) == {'bar': ['foo'], 'foo': ['bar']}


def test_add_qs_to_identical():
    orig = QueryDict(mutable=True)
    orig.update({'bar': 'foo', 'foo': 'bar'})
    params = _add_qs(orig, foo='bar', bar='foo')
    assert dict(params) == {'bar': ['foo'], 'foo': ['bar']}


def test_add_qs_to_existing():
    orig = QueryDict(mutable=True)
    orig.update({'foo': 'val1'})
    params = _add_qs(orig, foo='val2')
    assert dict(params) == {'foo': ['val1', 'val2']}


def test_replace_qs_to_empty():
    params = _replace_qs(QueryDict(mutable=True), foo='bar')
    assert dict(params) == {'foo': ['bar']}


def test_replace_qs_to_identical():
    orig = QueryDict(mutable=True)
    orig.update({'foo': 'bar'})
    params = _replace_qs(orig, foo='bar')
    assert dict(params) == {'foo': ['bar']}


def test_replace_qs_to_existing():
    orig = QueryDict(mutable=True)
    orig.update({'foo': 'val1'})
    params = _replace_qs(orig, foo='val2')
    assert dict(params) == {'foo': ['val2']}


def test_remove_qs_to_empty():
    params = _remove_qs(QueryDict(mutable=True), foo='bar')
    assert dict(params) == {}


def test_remove_qs_to_not_existing():
    orig = QueryDict(mutable=True)
    orig.update({'bar': 'foo'})
    params = _remove_qs(orig, foo='bar')
    assert dict(params) == {'bar': ['foo']}


def test_remove_qs_to_value_not_existing():
    orig = QueryDict(mutable=True)
    orig.update({'bar': 'foo'})
    params = _remove_qs(orig, bar='bar')
    assert dict(params) == {'bar': ['foo']}


def test_remove_qs_to_one():
    orig = QueryDict(mutable=True)
    orig.update({'foo': 'val1'})

    params = _remove_qs(orig, foo='val1')
    assert dict(params) == {}


def test_remove_qs_to_several():
    orig = QueryDict(mutable=True)
    orig.update({'foo': 'val1'})
    orig.update({'foo': 'val2'})
    assert dict(orig) == {'foo': ['val1', 'val2']}
    params = _remove_qs(orig, foo='val2')
    assert dict(params) == {'foo': ['val1']}
