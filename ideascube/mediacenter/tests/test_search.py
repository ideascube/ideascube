# -*- coding: utf-8 -*-
import pytest

from ..models import Document

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('cleansearch')
def test_document_are_indexed(video):
    assert Document.SearchModel.objects.count() == 1
    assert len(list(Document.SearchModel.search(public=True))) == 1
    assert Document.objects.search("Ikinyugunyugu").count() == 0
    video.title = "Ikinyugunyugu"
    video.save()
    assert Document.SearchModel.objects.count() == 1
    assert Document.objects.search("Ikinyugunyugu").count() == 1


@pytest.mark.usefixtures('cleansearch')
def test_hard_delete_is_deindexed(video):
    assert Document.SearchModel.objects.count() == 1
    video.delete()
    assert Document.SearchModel.objects.count() == 0
