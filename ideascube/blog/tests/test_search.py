# -*- coding: utf-8 -*-
import pytest

from ..models import Content

pytestmark = pytest.mark.django_db


def test_nothing_is_indexed_without_any_fixture():
    assert Content.objects.count() == 0


@pytest.mark.usefixtures('cleansearch')
def test_draft_is_indexed(draft):
    assert Content.objects.count() == 1
    assert len(list(Content.SearchModel.search(public=True))) == 0


@pytest.mark.usefixtures('cleansearch')
def test_deleted_is_indexed(deleted):
    assert Content.objects.count() == 1
    assert len(list(Content.SearchModel.search(public=True))) == 0


@pytest.mark.usefixtures('cleansearch')
def test_published_is_indexed(published):
    assert Content.objects.count() == 1
    assert len(list(Content.SearchModel.search(public=True))) == 1
    assert Content.objects.search(text__match="Ikinyugunyugu").count() == 0
    published.title = "Ikinyugunyugu"
    published.save()
    assert Content.objects.count() == 1
    assert Content.objects.search(text__match="Ikinyugunyugu").count() == 1


@pytest.mark.usefixtures('cleansearch')
def test_hard_delete_is_deindexed(published):
    assert Content.objects.count() == 1
    published.delete()
    assert Content.objects.count() == 0


@pytest.mark.usefixtures('cleansearch')
def test_search_is_case_unsensitive(published):
    published.title = "Ikinyugunyugu"
    published.save()
    assert Content.objects.search(text__match="ikinyugunyugu").count() == 1


@pytest.mark.usefixtures('cleansearch')
def test_we_can_search_arabic_content(published):
    published.title = "أكثر من خمسين لغة،"
    published.save()
    assert Content.objects.search(text__match="خمسين").count() == 1


@pytest.mark.usefixtures('cleansearch')
def test_we_can_search_with_joker(published):
    published.title = "Ikinyugunyugu"
    published.save()
    assert Content.objects.search(text__match="Ikinyug*").count() == 1


@pytest.mark.usefixtures('cleansearch')
def test_we_can_filter_search(published, draft):
    published.title = "A title with the moon"
    published.save()
    draft.title = "A moon in the title"
    draft.save()
    assert Content.objects.search(text__match='moon').count() == 2
    assert Content.objects.search(text__match='moon').published().count() == 1
    assert Content.objects.search(text__match='moon', public=True).count() == 1
    assert published in Content.objects.search(text__match='moon').published()
