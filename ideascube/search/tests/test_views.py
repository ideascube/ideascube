import pytest

from django.core.urlresolvers import reverse

from ideascube.blog.tests.factories import ContentFactory
from ideascube.blog.models import Content
from ideascube.library.tests.factories import BookFactory

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('cleansearch')
def test_search_view_should_show_results(app):
    content = ContentFactory(title='test content', status=Content.PUBLISHED)
    form = app.get(reverse('search:search')).forms['search']
    form['q'] = 'test'
    page = form.submit()
    assert content.title in page.content.decode()


@pytest.mark.usefixtures('cleansearch')
def test_search_view_should_not_return_draft_content_to_anonymous(app):
    content = ContentFactory(title='test content', status=Content.DRAFT)
    form = app.get(reverse('search:search')).forms['search']
    form['q'] = 'test'
    page = form.submit()
    assert content.title not in page.content.decode()


@pytest.mark.usefixtures('cleansearch')
def test_search_view_should_not_return_deleted_content_to_anonymous(app):
    content = ContentFactory(title='test content', status=Content.DELETED)
    form = app.get(reverse('search:search')).forms['search']
    form['q'] = 'test'
    page = form.submit()
    assert content.title not in page.content.decode()


@pytest.mark.usefixtures('cleansearch')
def test_search_view_should_not_return_draft_content_to_logged_user(loggedapp):
    content = ContentFactory(title='test content', status=Content.DRAFT)
    form = loggedapp.get(reverse('search:search')).forms['search']
    form['q'] = 'test'
    page = form.submit()
    assert content.title not in page.content.decode()


@pytest.mark.usefixtures('cleansearch')
def test_search_view_should_not_return_deleted_to_logged_user(loggedapp):
    content = ContentFactory(title='test content', status=Content.DELETED)
    form = loggedapp.get(reverse('search:search')).forms['search']
    form['q'] = 'test'
    page = form.submit()
    assert content.title not in page.content.decode()


@pytest.mark.usefixtures('cleansearch')
def test_search_view_should_return_draft_content_to_staff_user(staffapp):
    content = ContentFactory(title='test content', status=Content.DRAFT)
    form = staffapp.get(reverse('search:search')).forms['search']
    form['q'] = 'test'
    page = form.submit()
    assert content.title in page.content.decode()


@pytest.mark.usefixtures('cleansearch')
def test_search_view_should_not_return_deleted_to_staff_user(staffapp):
    content = ContentFactory(title='test content', status=Content.DELETED)
    form = staffapp.get(reverse('search:search')).forms['search']
    form['q'] = 'test'
    page = form.submit()
    assert content.title in page.content.decode()


@pytest.mark.usefixtures('cleansearch')
def test_search_view_should_return_mixed_content(app):
    content = ContentFactory(title='test content', status=Content.PUBLISHED)
    book = BookFactory(name='test book')
    form = app.get(reverse('search:search')).forms['search']
    form['q'] = 'test'
    page = form.submit()
    assert content.title in page.content.decode()
    assert book.name in page.content.decode()
