import pytest

from ideastube.blog.tests.factories import ContentFactory
from ideastube.library.tests.factories import BookFactory
from ideastube.blog.models import Content
from ideastube.library.models import Book

from ..templatetags.ideastube_tags import theme_slug, remove_i18n, tag_cloud, fa, do_min

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
