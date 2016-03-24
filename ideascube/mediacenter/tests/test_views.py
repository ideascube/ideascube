import pytest

from django.core.urlresolvers import reverse
from webtest import Upload

from ..views import Index
from ..models import Document
from .factories import DocumentFactory

pytestmark = pytest.mark.django_db


def test_anonymous_should_access_index_page(app, video):
    response = app.get(reverse('mediacenter:index'), status=200)
    assert video.title in response.content.decode()


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


def test_pagination_should_keep_querystring(app, monkeypatch):
    monkeypatch.setattr(Index, 'paginate_by', 2)
    DocumentFactory.create_batch(size=4, kind=Document.IMAGE)
    url = '{}?kind=image'.format(reverse('mediacenter:index'))
    response = app.get(url)
    link = response.pyquery.find('.next')
    assert link
    assert 'kind=image' in link[0].attrib['href']


def test_index_page_should_have_search_box(app, video):
    DocumentFactory(title="I'm a scorpion")
    response = app.get(reverse('mediacenter:index'), status=200)
    form = response.forms['search']
    form['q'] = "scorpion"
    response = form.submit()
    assert "scorpion" in response.content.decode()
    assert video.title not in response.content.decode()


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
    form['original'] = Upload('image.jpg', b'xxxxxx', 'image/jpeg')
    form.submit().follow()
    assert Document.objects.count() == 1


def test_can_create_app_document(staffapp):
    assert not Document.objects.count()
    url = reverse('mediacenter:document_create')
    form = staffapp.get(url).forms['model_form']
    form['title'] = 'my document title'
    form['summary'] = 'my document summary'
    form['credits'] = 'my document credits'
    form['kind'] = Document.APP
    form['original'] = Upload('soft.exe', b'xxxxxx',
                              'application/x-msdos-program')
    form.submit().follow()
    assert Document.objects.count() == 1


def test_can_create_document_without_lang(staffapp):
    assert not Document.objects.count()
    url = reverse('mediacenter:document_create')
    form = staffapp.get(url).forms['model_form']
    form['title'] = 'my document title'
    form['summary'] = 'my document summary'
    form['credits'] = 'my document credits'
    form['original'] = Upload('image.jpg', b'xxxxxx', 'image/jpeg')
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
    form['original'] = Upload('audio.mp3', b'xxxxxx', 'image/jpeg')
    form.submit().follow()
    assert Document.objects.first().kind == Document.IMAGE


def test_uploading_without_content_type_should_be_ok(staffapp):
    assert not Document.objects.count()
    url = reverse('mediacenter:document_create')
    form = staffapp.get(url).forms['model_form']
    form['title'] = 'my document title'
    form['summary'] = 'my document summary'
    form['credits'] = 'my document credits'
    form['original'] = Upload('audio.mp3', b'xxxxxx')
    form.submit().follow()
    assert Document.objects.count() == 1


def test_oembed_should_return_video_oembed_extract(app, video):
    url = '{base}?url=http://testserver{media}'.format(
        base=reverse('mediacenter:oembed'),
        media=reverse('mediacenter:document_detail', kwargs={'pk': video.pk})
        )
    resp = app.get(url, extra_environ={'SERVER_NAME': 'testserver'})
    assert 'video' in resp.content.decode()
    assert 'source' in resp.content.decode()
    assert video.original.url in resp.content.decode()


def test_oembed_should_return_image_oembed_extract(app, image):
    url = '{base}?url=http://testserver{media}'.format(
        base=reverse('mediacenter:oembed'),
        media=reverse('mediacenter:document_detail', kwargs={'pk': image.pk})
        )
    resp = app.get(url, extra_environ={'SERVER_NAME': 'testserver'})
    assert 'img' in resp.content.decode()
    assert 'src' in resp.content.decode()
    assert image.original.url in resp.content.decode()


def test_oembed_should_return_pdf_oembed_extract(app, pdf):
    url = '{base}?url=http://testserver{media}'.format(
        base=reverse('mediacenter:oembed'),
        media=reverse('mediacenter:document_detail', kwargs={'pk': pdf.pk})
        )
    resp = app.get(url, extra_environ={'SERVER_NAME': 'testserver'})
    assert pdf.original.url in resp.content.decode()


def test_by_tag_page_should_be_filtered_by_tag(app):
    plane = DocumentFactory(tags=['plane'])
    boat = DocumentFactory(tags=['boat'])
    response = app.get(reverse('mediacenter:index'), {'tags': 'plane'})
    assert plane.title in response.content.decode()
    assert boat.title not in response.content.decode()


def test_by_tag_page_is_paginated(app, monkeypatch):
    monkeypatch.setattr(Index, 'paginate_by', 2)
    DocumentFactory.create_batch(size=4, tags=['plane'])
    url = reverse('mediacenter:index')
    response = app.get(url, {'tags':'plane'})
    assert response.pyquery.find('.pagination')
    assert response.pyquery.find('.next')
    assert not response.pyquery.find('.previous')
    response = app.get(url + '?page=2')
    assert response.pyquery.find('.pagination')
    assert not response.pyquery.find('.next')
    assert response.pyquery.find('.previous')
    response = app.get(url + '?page=3', status=404)


def test_can_create_document_with_tags(staffapp):
    url = reverse('mediacenter:document_create')
    form = staffapp.get(url).forms['model_form']
    form['title'] = 'my document title'
    form['summary'] = 'my document summary'
    form['credits'] = 'my document credits'
    form['original'] = Upload('image.jpg', b'xxxxxx', 'image/jpeg')
    form['tags'] = 'tag1, tag2'
    form.submit().follow()
    doc = Document.objects.last()
    assert doc.tags.count() == 2
    assert doc.tags.first().name == 'tag1'


def test_can_update_document_tags(staffapp, pdf):
    assert pdf.tags.count() == 0
    url = reverse('mediacenter:document_update', kwargs={'pk': pdf.pk})
    form = staffapp.get(url).forms['model_form']
    form['tags'] = 'tag1, tag2'
    form.submit().follow()
    doc = Document.objects.get(pk=pdf.pk)
    assert doc.tags.count() == 2
    assert doc.tags.first().name == 'tag1'
