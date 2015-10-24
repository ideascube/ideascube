# -*- coding: utf-8 -*-
import pytest

from ideastube.blog.tests.factories import ContentFactory
from ideastube.blog.models import Content
from ..models import Search


pytestmark = pytest.mark.django_db


def test_nothing_is_indexed_without_any_fixture():
    assert Search.objects.count() == 0


def test_searchable_model_is_indexed():
    assert Content.objects.count() == 0
    content = ContentFactory(title="music")
    assert Content.objects.count() == 1
    assert content in Search.search(text__match="music")


def test_more_relevant_should_come_first():
    second = ContentFactory(title="About music and music")
    third = ContentFactory(title="About music")
    first = ContentFactory(title="About music and music but also music")
    assert Content.objects.count() == 3
    assert first == list(Search.search(text__match="music"))[0]
    assert second == list(Search.search(text__match="music"))[1]
    assert third == list(Search.search(text__match="music"))[2]


def test_ids_only_returns_ids():
    content = ContentFactory(title="music")
    assert content.pk in Search.ids(text__match="music")


def test_we_can_search_on_non_fts_fields_only():
    content = ContentFactory(title="music")
    assert content in Search.search(public=False)
