# -*- coding: utf-8 -*-
import pytest

from ideascube.blog.tests.factories import ContentFactory
from ideascube.blog.models import Content
from ideascube.mediacenter.models import Document
from ideascube.mediacenter.tests.factories import DocumentFactory
from ..models import Search


pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('cleansearch')
def test_nothing_is_indexed_without_any_fixture():
    assert Search.objects.count() == 0


@pytest.mark.usefixtures('cleansearch')
def test_searchable_model_is_indexed():
    assert Content.objects.count() == 0
    content = ContentFactory(title="music")
    assert Content.objects.count() == 1
    assert content in Search.search(text__match="music")


@pytest.mark.usefixtures('cleansearch')
def test_search_Document_on_lang():
    assert Document.objects.count() == 0
    document = DocumentFactory(lang="FR")
    assert Document.objects.count() == 1
    assert document in Search.search(lang="FR")
    assert document not in Search.search(lang="EN")


@pytest.mark.usefixtures('cleansearch')
def test_search_Document_on_kind():
    assert Document.objects.count() == 0
    document = DocumentFactory(kind="video")
    assert Document.objects.count() == 1
    assert document in Search.search(kind="video")
    assert document not in Search.search(kind="pdf")


@pytest.mark.usefixtures('cleansearch')
def test_search_Document_on_tag():
    assert Document.objects.count() == 0
    document = DocumentFactory(tags=["foo"])
    document_no_tag = DocumentFactory()
    assert Document.objects.count() == 2

    assert document in Search.search(tags__match=["foo"])
    assert document_no_tag not in Search.search(tags__match=["foo"])

    assert document not in Search.search(tags__match=["bar"])
    assert document_no_tag not in Search.search(tags__match=["bar"])


@pytest.mark.usefixtures('cleansearch')
def test_search_Document_on_no_tag():
    assert Document.objects.count() == 0
    document = DocumentFactory(tags=["foo"])
    document_no_tag = DocumentFactory()
    assert Document.objects.count() == 2

    assert document not in Search.search(tags__match=[])
    assert document_no_tag in Search.search(tags__match=[])


@pytest.mark.usefixtures('cleansearch')
def test_search_Document_multiple_tag():
    doc_foo = DocumentFactory(tags=["foo"])
    doc_bar = DocumentFactory(tags=["bar"])
    doc_foo_bar = DocumentFactory(tags=["foo", "bar"])
    doc_bar_foo = DocumentFactory(tags=["bar", "foo"])
    doc = DocumentFactory()

    for d in (doc_foo, doc_foo_bar, doc_bar_foo):
        assert d in Search.search(tags__match=["foo"])
    for d in (doc, doc_bar):
        assert d not in Search.search(tags__match=["foo"])

    for d in (doc_bar, doc_foo_bar, doc_bar_foo):
        assert d in Search.search(tags__match=["bar"])
    for d in (doc, doc_foo):
        assert d not in Search.search(tags__match=["bar"])

    for d in (doc_foo_bar, doc_bar_foo):
        assert d in Search.search(tags__match=["bar", "foo"])
    for d in (doc, doc_foo, doc_bar):
        assert d not in Search.search(tags__match=["bar", "foo"])

    for d in (doc_foo_bar, doc_bar_foo):
        assert d in Search.search(tags__match=["foo", "bar"])
    for d in (doc, doc_foo, doc_bar):
        assert d not in Search.search(tags__match=["foo", "bar"])


@pytest.mark.usefixtures('cleansearch')
def test_more_relevant_should_come_first():
    second = ContentFactory(title="About music and music")
    third = ContentFactory(title="About music")
    first = ContentFactory(title="About music and music but also music")
    assert Content.objects.count() == 3
    assert first == list(Search.search(text__match="music"))[0]
    assert second == list(Search.search(text__match="music"))[1]
    assert third == list(Search.search(text__match="music"))[2]


@pytest.mark.usefixtures('cleansearch')
def test_ids_only_returns_ids():
    content = ContentFactory(title="music")
    assert content.pk in Search.ids(text__match="music")


@pytest.mark.usefixtures('cleansearch')
def test_we_can_search_on_non_fts_fields_only():
    content = ContentFactory(title="music")
    assert content in Search.search(public=False)
