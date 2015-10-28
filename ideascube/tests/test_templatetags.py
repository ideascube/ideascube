# -*- coding: utf-8 -*-
import pytest

from ideascube.blog.models import Content
from ideascube.blog.tests.factories import ContentFactory
from ideascube.library.models import Book
from ideascube.library.tests.factories import BookFactory

from ..templatetags.ideascube_tags import (do_min, fa, remove_i18n,
                                           smart_truncate, tag_cloud,
                                           theme_slug)

pytestmark = pytest.mark.django_db


def test_theme_slug_for_content():
    content = ContentFactory()
    assert theme_slug(content) == '<span class="theme create">blog</span>'


def test_theme_slug_for_book():
    book = BookFactory()
    assert theme_slug(book) == '<span class="theme read">book</span>'


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


def test_tag_cloud_should_return_most_common_tags():
    ContentFactory(tags=['plane', 'boat'])
    ContentFactory(tags=['plane', 'bike'])
    ContentFactory(tags=['plane', 'boat'])
    context = tag_cloud('xxxx', limit=2)
    tags = [t.name for t in context['tags']]
    assert tags[0] == 'plane'
    assert tags[1] == 'boat'


def test_tag_cloud_should_be_filtered_by_model_if_given():
    ContentFactory(tags=['plane', 'boat'])
    BookFactory(tags=['bike', 'boat'])
    context = tag_cloud('xxxx', limit=2, model=Content)
    assert [t.name for t in context['tags']] == ['boat', 'plane']
    context = tag_cloud('xxxx', limit=2, model=Book)
    assert [t.name for t in context['tags']] == ['bike', 'boat']


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
