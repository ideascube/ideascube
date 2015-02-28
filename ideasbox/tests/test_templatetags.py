import pytest

from ideasbox.blog.tests.factories import ContentFactory
from ideasbox.library.tests.factories import BookFactory

from ..templatetags.ideasbox_tags import theme_slug, remove_i18n, fa

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
