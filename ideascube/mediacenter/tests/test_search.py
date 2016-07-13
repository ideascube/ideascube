# -*- coding: utf-8 -*-
import pytest

from ideascube.search.models import Search

from ..models import Document

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('cleansearch')
def test_document_are_indexed(video):
    assert Search.objects.count() == 1
    assert len(list(Search.search(public=True))) == 1
    assert Document.objects.search("Ikinyugunyugu").count() == 0
    video.title = "Ikinyugunyugu"
    video.save()
    assert Search.objects.count() == 1
    assert Document.objects.search("Ikinyugunyugu").count() == 1


@pytest.mark.usefixtures('cleansearch')
def test_hard_delete_is_deindexed(video):
    assert Search.objects.count() == 1
    video.delete()
    assert Search.objects.count() == 0
