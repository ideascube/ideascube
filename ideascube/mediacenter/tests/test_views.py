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
    response = app.get(reverse('mediacenter:index'), {'kind': 'image'})
    link = response.pyquery.find('.next')
    assert link
    assert 'kind=image' in link[0].attrib['href']


def test_only_kind_with_content_should_appear(app, pdf, image):
    response = app.get(reverse('mediacenter:index'))
    links = response.pyquery('a').filter(lambda i, elem: elem.text == 'pdf')
    assert len(links) == 1

    links = response.pyquery('a').filter(lambda i, elem: elem.text == 'image')
    assert len(links) == 1

    links = response.pyquery('a').filter(lambda i, elem: elem.text == 'video')
    assert len(links) == 0

    links = response.pyquery('a').filter(lambda i, elem: elem.text == 'audio')
    assert len(links) == 0

def test_search_box_should_update_querystring(app):
    response = app.get(reverse('mediacenter:index'),
                       {'kind': 'image', 'q': 'bar'})
    form = response.forms['search']
    form['q'] = "foo"
    response = form.submit()
    assert {'kind': 'image', 'q': 'foo'} == response.request.GET

def test_kind_link_should_no_be_displayed_if_no_several_kinds(app):
    response = app.get(reverse('mediacenter:index'))
    links = response.pyquery('a').filter(lambda i, elem: elem.text == 'pdf')
    assert len(links) == 0

    DocumentFactory(kind='pdf')
    response = app.get(reverse('mediacenter:index'))
    links = response.pyquery('a').filter(lambda i, elem: elem.text == 'pdf')
    assert len(links) == 0

    DocumentFactory(kind='image')
    response = app.get(reverse('mediacenter:index'))
    links = response.pyquery('a').filter(lambda i, elem: elem.text == 'pdf')
    assert len(links) == 1

def test_lang_link_should_no_be_displayed_if_no_several_langs(app):
    response = app.get(reverse('mediacenter:index'))
    links = response.pyquery('a').filter(lambda i, elem: elem.text == 'Français')
    assert len(links) == 0

    DocumentFactory(lang='fr')
    response = app.get(reverse('mediacenter:index'))
    links = response.pyquery('a').filter(lambda i, elem: elem.text == 'Français')
    assert len(links) == 0

    DocumentFactory(lang='en')
    response = app.get(reverse('mediacenter:index'))
    links = response.pyquery('a').filter(lambda i, elem: elem.text == 'Français')
    assert len(links) == 1

def test_kind_link_should_update_querystring(app, pdf, image):
    response = app.get(reverse('mediacenter:index'),
                       {'kind': 'image', 'q': 'bar'})
    links = response.pyquery('a').filter(lambda i, elem: elem.text == 'pdf')
    response = app.get("{}{}".format(reverse('mediacenter:index'),
                                     links[0].attrib['href']),
                       status=200)
    assert {'kind': 'pdf', 'q': 'bar'} == response.request.GET


def test_lang_link_should_update_querystring(app):
    DocumentFactory(lang='fr')
    DocumentFactory(lang='en')
    response = app.get(reverse('mediacenter:index'), {'lang': 'en', 'q': 'bar'})
    links = response.pyquery('a').filter(lambda i, elem: elem.text == 'Français')
    response = app.get("{}{}".format(reverse('mediacenter:index'),
                                     links[0].attrib['href']),
                       status=200)
    assert {'lang': 'fr', 'q': 'bar'} == response.request.GET


def test_tags_link_should_update_querystring(app):
    DocumentFactory(lang='en', tags=['tag1', 'tag2', 'tag3'])
    response = app.get(reverse('mediacenter:index'), {'lang': 'en'})

    links = response.pyquery('.card a').filter(
        lambda i, elem: (elem.text or '').strip() == 'tag1')
    print(links[0].attrib['href'])
    response = app.get(links[0].attrib['href'], status=200)
    assert {'lang': 'en', 'tags': 'tag1'} == response.request.GET

    links = response.pyquery('.card a').filter(
        lambda i, elem: (elem.text or '').strip() == 'tag2')
    print(links[0].attrib['href'])
    response = app.get(links[0].attrib['href'], status=200)
    assert {'lang': ['en'], 'tags': ['tag1', 'tag2']} == \
        response.request.GET.dict_of_lists()

    # Do it a second time. Only one 'tag2' should be present
    links = response.pyquery('.card a').filter(
        lambda i, elem: (elem.text or '').strip() == 'tag2')
    print(links[0].attrib['href'])
    response = app.get(links[0].attrib['href'], status=200)
    assert {'lang': ['en'], 'tags': ['tag1', 'tag2']} == \
        response.request.GET.dict_of_lists()


def test_remove_filter_should_be_present(app):
    response = app.get(reverse('mediacenter:index'),
                       {'lang': 'en',
                        'q': 'foo',
                        'tags': ['tag1', 'tag2'],
                        'kind': 'video'
                       })

    links = response.pyquery('.filter-card a').filter(
        lambda i, elem: "English" in (elem.text or ''))
    assert links
    resp = app.get("{}{}".format(reverse('mediacenter:index'),
                                 links[0].attrib['href']),
                   status=200)
    assert {'q': ['foo'], 'tags': ['tag1', 'tag2'], 'kind': ['video']} == \
        resp.request.GET.dict_of_lists()

    links = response.pyquery('.filter-card a').filter(
        lambda i, elem: "foo" in (elem.text or ''))
    assert links
    resp = app.get("{}{}".format(reverse('mediacenter:index'),
                                 links[0].attrib['href']),
                   status=200)
    assert {'lang': ['en'], 'tags': ['tag1', 'tag2'], 'kind': ['video']} == \
        resp.request.GET.dict_of_lists()

    links = response.pyquery('.filter-card a').filter(
        lambda i, elem: "tag1" in (elem.text or ''))
    assert links
    resp = app.get("{}{}".format(reverse('mediacenter:index'),
                                 links[0].attrib['href']),
                   status=200)
    assert {'lang': ['en'], 'q': ['foo'], 'tags': ['tag2'], 'kind': ['video']} \
        == resp.request.GET.dict_of_lists()

    links = response.pyquery('.filter-card a').filter(
        lambda i, elem: "tag2" in (elem.text or ''))
    assert links
    resp = app.get("{}{}".format(reverse('mediacenter:index'),
                                 links[0].attrib['href']),
                   status=200)
    assert {'lang': ['en'], 'q': ['foo'], 'tags': ['tag1'], 'kind': ['video']} \
        == resp.request.GET.dict_of_lists()

    links = response.pyquery('.filter-card a').filter(
        lambda i, elem: "video" in (elem.text or ''))
    assert links
    resp = app.get("{}{}".format(reverse('mediacenter:index'),
                                 links[0].attrib['href']),
                   status=200)
    assert {'lang': ['en'], 'q': ['foo'], 'tags': ['tag1', 'tag2']} == \
        resp.request.GET.dict_of_lists()


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
    DocumentFactory.create_batch(size=2)
    url = reverse('mediacenter:index')
    response = app.get(url, {'tags': 'plane'})
    assert response.pyquery.find('.pagination')
    assert response.pyquery.find('.next')
    assert not response.pyquery.find('.previous')
    response = app.get(url + '?tags=plane&page=2')
    assert response.pyquery.find('.pagination')
    assert not response.pyquery.find('.next')
    assert response.pyquery.find('.previous')
    app.get(url + '?tags=plane&page=3', status=404)
    app.get(url + '?page=3', status=200)


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
