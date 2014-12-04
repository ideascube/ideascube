import pytest

from django.core.urlresolvers import reverse

from ..models import Book, BookSpecimen
from ..views import Index
from .factories import BookSpecimenFactory, BookFactory

pytestmark = pytest.mark.django_db


def test_anonymous_should_access_index_page(app):
    assert app.get(reverse('library:index'), status=200)


def test_only_books_with_specimen_should_be_in_index(app, book, specimen):
    response = app.get(reverse('library:index'))
    assert specimen.book.title in response.content
    assert book.title not in response.content


def test_index_page_is_paginated(app, monkeypatch):
    monkeypatch.setattr(Index, 'paginate_by', 2)
    for i in xrange(4):
        BookSpecimenFactory()
    response = app.get(reverse('library:index'))
    assert response.pyquery.find('.pagination')
    assert response.pyquery.find('.next')
    assert not response.pyquery.find('.previous')
    response = app.get(reverse('library:index') + '?page=2')
    assert response.pyquery.find('.pagination')
    assert not response.pyquery.find('.next')
    assert response.pyquery.find('.previous')
    response = app.get(reverse('library:index') + '?page=3', status=404)


def test_everyone_should_access_book_detail_page(app, book):
    assert app.get(reverse('library:book_detail',
                           kwargs={'pk': book.pk}), status=200)


def test_anonymous_should_not_access_book_create_page(app):
    assert app.get(reverse('library:book_create'), status=302)


def test_non_staff_should_not_access_book_create_page(loggedapp):
    assert loggedapp.get(reverse('library:book_create'), status=302)


def test_staff_should_access_book_create_page(staffapp):
    assert staffapp.get(reverse('library:book_create'), status=200)


def test_anonymous_should_not_access_book_update_page(app, book):
    assert app.get(reverse('library:book_update',
                   kwargs={'pk': book.pk}), status=302)


def test_non_staff_should_not_access_book_update_page(loggedapp, book):
    assert loggedapp.get(reverse('library:book_update',
                         kwargs={'pk': book.pk}), status=302)


def test_anonymous_should_not_access_book_delete_page(app, book):
    assert app.get(reverse('library:book_delete',
                   kwargs={'pk': book.pk}), status=302)


def test_non_staff_should_not_access_book_delete_page(loggedapp, book):
    assert loggedapp.get(reverse('library:book_delete',
                         kwargs={'pk': book.pk}), status=302)


def test_anonymous_should_not_access_specimen_delete_page(app, book):
    assert app.get(reverse('library:specimen_delete',
                   kwargs={'pk': book.pk}), status=302)


def test_non_staff_should_not_access_specimen_delete_page(loggedapp, book):
    assert loggedapp.get(reverse('library:specimen_delete',
                         kwargs={'pk': book.pk}), status=302)


def test_staff_should_access_book_update_page(staffapp, book):
    assert staffapp.get(reverse('library:book_update',
                        kwargs={'pk': book.pk}), status=200)


def test_staff_can_create_book(staffapp):
    form = staffapp.get(reverse('library:book_create')).form
    assert not Book.objects.all()
    form['title'] = 'My book title'
    form['summary'] = 'My book summary'
    form['section'] = '1'
    form.submit().follow()
    assert Book.objects.all()


def test_staff_can_edit_book(staffapp, book):
    form = staffapp.get(reverse('library:book_update',
                                kwargs={'pk': book.pk})).form
    title = "New title"
    assert Book.objects.get(pk=book.pk).title != title
    form['title'] = title
    form.submit().follow()
    assert Book.objects.get(pk=book.pk).title == title


def test_staff_user_can_delete_book(staffapp, book):
    assert len(Book.objects.all()) == 1
    url = reverse('library:book_delete', kwargs={'pk': book.pk})
    form = staffapp.get(url).form
    form.submit()
    assert len(Book.objects.all()) == 0


def test_staff_can_create_specimen(staffapp, book):
    url = reverse('library:specimen_create', kwargs={'book_pk': book.pk})
    form = staffapp.get(url).form
    assert not BookSpecimen.objects.all()
    assert not book.specimen.all()
    form['serial'] = '23135321'
    form.submit().follow()
    assert BookSpecimen.objects.all()
    assert book.specimen.all()


def test_staff_can_edit_specimen(staffapp, specimen):
    form = staffapp.get(reverse('library:specimen_update',
                                kwargs={'pk': specimen.pk})).form
    remarks = "This is a new remark"
    assert BookSpecimen.objects.get(pk=specimen.pk).remarks != remarks
    form['remarks'] = remarks
    form.submit().follow()
    assert BookSpecimen.objects.get(pk=specimen.pk).remarks == remarks


def test_staff_user_can_delete_specimen(staffapp, specimen):
    assert len(BookSpecimen.objects.all()) == 1
    assert len(Book.objects.all()) == 1
    url = reverse('library:specimen_delete', kwargs={'pk': specimen.pk})
    form = staffapp.get(url).form
    form.submit()
    assert len(Book.objects.all()) == 1
    assert not BookSpecimen.objects.all()


def test_it_should_be_possible_to_create_several_books_without_isbn(staffapp):
    assert not Book.objects.all()
    url = reverse('library:book_create')
    form = staffapp.get(url).form
    form['title'] = 'My book title'
    form['summary'] = 'My book summary'
    form['section'] = '1'
    form['isbn'] = ''
    form.submit().follow()
    form = staffapp.get(url).form
    form['title'] = 'My book title 2'
    form['summary'] = 'My book summary 2'
    form['section'] = '2'
    form['isbn'] = ''
    form.submit().follow()
    assert len(Book.objects.all()) == 2


def test_it_should_be_possible_to_remove_isbn_from_books(staffapp):
    book1 = BookFactory(isbn='123456')
    book2 = BookFactory(isbn='321564987')
    assert not Book.objects.filter(isbn__isnull=True)
    form = staffapp.get(reverse('library:book_update',
                        kwargs={'pk': book1.pk})).form
    form['isbn'] = ''
    form.submit().follow()
    form = staffapp.get(reverse('library:book_update',
                        kwargs={'pk': book2.pk})).form
    form['isbn'] = ''
    form.submit().follow()
    assert len(Book.objects.filter(isbn__isnull=True)) == 2
