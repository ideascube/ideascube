import pytest

from django.core.urlresolvers import reverse
from webtest import Upload

from ..views import Index
from ..models import Document
from .factories import DocumentFactory

pytestmark = pytest.mark.django_db


def test_anonymous_should_access_index_page(app, video):
    response = app.get(reverse('mediacenter:index'), status=200)
    assert video.title in response.content


def test_index_page_is_paginated(app, monkeypatch):
    monkeypatch.setattr(Index, 'paginate_by', 2)
    DocumentFactory.create_batch(size=4)
    response = app.get(reverse('mediacenter:index'))
    assert response.pyquery.find('.pagination')
    assert response.pyquery.find('.next')
    assert not response.pyquery.find('.previous')
    response = app.get(reverse('mediacenter:index') + '?page=2')
    assert response.pyquery.find('.pagination')
    assert not response.pyquery.find('.next')
    assert response.pyquery.find('.previous')
    response = app.get(reverse('mediacenter:index') + '?page=3', status=404)


def test_everyone_should_access_image_detail_page(app, image):
    assert app.get(reverse('mediacenter:document_detail',
                           kwargs={'pk': image.pk}), status=200)


def test_everyone_should_access_video_detail_page(app, video):
    assert app.get(reverse('mediacenter:document_detail',
                           kwargs={'pk': video.pk}), status=200)


def test_everyone_should_access_pdf_detail_page(app, pdf):
    assert app.get(reverse('mediacenter:document_detail',
                           kwargs={'pk': pdf.pk}), status=200)


def test_everyone_should_access_audio_detail_page(app, audio):
    assert app.get(reverse('mediacenter:document_detail',
                           kwargs={'pk': audio.pk}), status=200)


def test_everyone_should_access_text_detail_page(app, text):
    assert app.get(reverse('mediacenter:document_detail',
                           kwargs={'pk': text.pk}), status=200)


def test_everyone_should_access_other_detail_page(app, other):
    assert app.get(reverse('mediacenter:document_detail',
                           kwargs={'pk': other.pk}), status=200)


def test_anonymous_should_not_access_edit_page(app, video):
    assert app.get(reverse('mediacenter:document_update',
                           kwargs={'pk': video.pk}), status=302)


def test_non_staff_should_not_access_edit_page(loggedapp, video):
    assert loggedapp.get(reverse('mediacenter:document_update',
                                 kwargs={'pk': video.pk}), status=302)


def test_staff_should_access_edit_page(staffapp, video):
    assert staffapp.get(reverse('mediacenter:document_update',
                                kwargs={'pk': video.pk}), status=200)


def test_staff_can_edit_document(staffapp, video):
    form = staffapp.get(reverse('mediacenter:document_update',
                                kwargs={'pk': video.pk})).forms['model_form']
    title = "New title"
    assert Document.objects.get(pk=video.pk).title != title
    form['title'] = title
    form.submit().follow()
    assert Document.objects.get(pk=video.pk).title == title


def test_can_create_document(staffapp):
    assert not Document.objects.count()
    url = reverse('mediacenter:document_create')
    form = staffapp.get(url).forms['model_form']
    form['title'] = 'my document title'
    form['summary'] = 'my document summary'
    form['credits'] = 'my document credits'
    form['original'] = Upload('image.jpg', 'xxxxxx', 'image/jpeg')
    form.submit().follow()
    assert Document.objects.count() == 1


def test_can_create_document_without_lang(staffapp):
    assert not Document.objects.count()
    url = reverse('mediacenter:document_create')
    form = staffapp.get(url).forms['model_form']
    form['title'] = 'my document title'
    form['summary'] = 'my document summary'
    form['credits'] = 'my document credits'
    form['original'] = Upload('image.jpg', 'xxxxxx', 'image/jpeg')
    form['lang'] = ''
    form.submit().follow()
    assert Document.objects.count() == 1


def test_content_type_should_have_priority_over_extension(staffapp):
    assert not Document.objects.count()
    url = reverse('mediacenter:document_create')
    form = staffapp.get(url).forms['model_form']
    form['title'] = 'my document title'
    form['summary'] = 'my document summary'
    form['credits'] = 'my document credits'
    form['original'] = Upload('audio.mp3', 'xxxxxx', 'image/jpeg')
    form.submit().follow()
    assert Document.objects.first().kind == Document.IMAGE


def test_uploading_without_content_type_should_be_ok(staffapp):
    assert not Document.objects.count()
    url = reverse('mediacenter:document_create')
    form = staffapp.get(url).forms['model_form']
    form['title'] = 'my document title'
    form['summary'] = 'my document summary'
    form['credits'] = 'my document credits'
    form['original'] = Upload('audio.mp3', 'xxxxxx')
    form.submit().follow()
    assert Document.objects.count() == 1
