import pytest

from django.core.urlresolvers import reverse

from ..views import Index
from ..models import Content
from .factories import ContentFactory

pytestmark = pytest.mark.django_db


def test_anonymous_should_access_index_page(app):
    assert app.get(reverse('blog:index'), status=200)


def test_only_published_should_be_in_index(app, published, draft, deleted):
    response = app.get(reverse('blog:index'))
    assert published.title in response.content
    assert draft.title not in response.content
    assert deleted.title not in response.content


def test_index_page_is_paginated(app, monkeypatch):
    monkeypatch.setattr(Index, 'paginate_by', 2)
    for i in xrange(4):
        ContentFactory(status=Content.PUBLISHED)
    response = app.get(reverse('blog:index'))
    assert response.pyquery.find('.pagination')
    assert response.pyquery.find('.next')
    assert not response.pyquery.find('.previous')
    response = app.get(reverse('blog:index') + '?page=2')
    assert response.pyquery.find('.pagination')
    assert not response.pyquery.find('.next')
    assert response.pyquery.find('.previous')
    response = app.get(reverse('blog:index') + '?page=3', status=404)


def test_everyone_should_access_published_content(app, published):
    assert app.get(reverse('blog:content_detail',
                           kwargs={'pk': published.pk}), status=200)


def test_anonymous_should_not_access_draft_content(app, draft):
    assert app.get(reverse('blog:content_detail', kwargs={'pk': draft.pk}),
                   status=404)


def test_non_staff_should_not_access_draft_content(loggedapp, draft):
    assert loggedapp.get(reverse('blog:content_detail',
                         kwargs={'pk': draft.pk}), status=404)


def test_staff_should_access_draft_content(staffapp, draft):
    assert staffapp.get(reverse('blog:content_detail',
                                kwargs={'pk': draft.pk}), status=200)


def test_anonymous_should_not_access_deleted_page(app, deleted):
    assert app.get(reverse('blog:content_detail', kwargs={'pk': deleted.pk}),
                   status=404)


def test_non_staff_should_not_access_delete_page(loggedapp, deleted):
    assert loggedapp.get(reverse('blog:content_detail',
                         kwargs={'pk': deleted.pk}), status=404)


def test_staff_should_access_deleted_content(staffapp, deleted):
    assert staffapp.get(reverse('blog:content_detail',
                                kwargs={'pk': deleted.pk}), status=200)


def test_anonymous_should_not_access_edit_page(app, published):
    assert app.get(reverse('blog:content_update',
                           kwargs={'pk': published.pk}), status=302)


def test_non_staff_should_not_access_edit_page(loggedapp, published):
    assert loggedapp.get(reverse('blog:content_update',
                                 kwargs={'pk': published.pk}), status=302)


def test_staff_should_access_published_edit_page(staffapp, published):
    assert staffapp.get(reverse('blog:content_update',
                                kwargs={'pk': published.pk}), status=200)


def test_staff_should_access_draft_edit_page(staffapp, draft):
    assert staffapp.get(reverse('blog:content_update',
                                kwargs={'pk': draft.pk}), status=200)


def test_staff_should_access_deleted_edit_page(staffapp, deleted):
    assert staffapp.get(reverse('blog:content_update',
                                kwargs={'pk': deleted.pk}), status=200)


def test_staff_can_edit_published_content(staffapp, published):
    form = staffapp.get(reverse('blog:content_update',
                                kwargs={'pk': published.pk})).form
    title = "New title"
    assert Content.objects.get(pk=published.pk).title != title
    form['title'] = title
    form.submit().follow()
    assert Content.objects.get(pk=published.pk).title == title


def test_staff_can_edit_draft_content(staffapp, draft):
    form = staffapp.get(reverse('blog:content_update',
                                kwargs={'pk': draft.pk})).form
    title = "New title"
    assert Content.objects.get(pk=draft.pk).title != title
    form['title'] = title
    form.submit().follow()
    assert Content.objects.get(pk=draft.pk).title == title


def test_staff_can_edit_delete_content(staffapp, deleted):
    form = staffapp.get(reverse('blog:content_update',
                                kwargs={'pk': deleted.pk})).form
    title = "New title"
    assert Content.objects.get(pk=deleted.pk).title != title
    form['title'] = title
    form.submit().follow()
    assert Content.objects.get(pk=deleted.pk).title == title
