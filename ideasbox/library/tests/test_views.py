import pytest
from django.core.urlresolvers import reverse
from webtest import Upload

from ..models import Book, BookSpecimen
from ..views import ByTag, Index
from .factories import BookFactory, BookSpecimenFactory

pytestmark = pytest.mark.django_db


def test_anonymous_should_access_index_page(app):
    assert app.get(reverse('library:index'), status=200)


def test_only_books_with_specimen_should_be_in_index(app, book, specimen):
    response = app.get(reverse('library:index'))
    assert specimen.book.title in response.content
    assert book.title not in response.content


def test_index_page_is_paginated(app, monkeypatch):
    monkeypatch.setattr(Index, 'paginate_by', 2)
    BookSpecimenFactory.create_batch(size=4)
    url = reverse('library:index')
    response = app.get(url)
    assert response.pyquery.find('.pagination')
    assert response.pyquery.find('.next')
    assert not response.pyquery.find('.previous')
    response = app.get('{url}?page=2'.format(url=url))
    assert response.pyquery.find('.pagination')
    assert not response.pyquery.find('.next')
    assert response.pyquery.find('.previous')
    response = app.get('{url}?page=3'.format(url=url), status=404)


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
    form = staffapp.get(reverse('library:book_create')).forms['model_form']
    assert not Book.objects.count()
    form['title'] = 'My book title'
    form['summary'] = 'My book summary'
    form['section'] = '1'
    form.submit().follow()
    assert Book.objects.count()


def test_staff_can_edit_book(staffapp, book):
    form = staffapp.get(reverse('library:book_update',
                                kwargs={'pk': book.pk})).forms['model_form']
    title = "New title"
    assert Book.objects.get(pk=book.pk).title != title
    form['title'] = title
    form.submit().follow()
    assert Book.objects.get(pk=book.pk).title == title


def test_staff_user_can_delete_book(staffapp, book):
    assert Book.objects.count() == 1
    url = reverse('library:book_delete', kwargs={'pk': book.pk})
    form = staffapp.get(url).forms['delete_form']
    form.submit()
    assert not Book.objects.count()


def test_staff_can_create_specimen(staffapp, book):
    url = reverse('library:specimen_create', kwargs={'book_pk': book.pk})
    form = staffapp.get(url).forms['model_form']
    assert not book.specimens.count()
    form['serial'] = '23135321'
    form.submit().follow()
    assert book.specimens.count()


def test_staff_can_edit_specimen(staffapp, specimen):
    url = reverse('library:specimen_update', kwargs={'pk': specimen.pk})
    form = staffapp.get(url).forms['model_form']
    remarks = "This is a new remark"
    assert BookSpecimen.objects.get(pk=specimen.pk).remarks != remarks
    form['remarks'] = remarks
    form.submit().follow()
    assert BookSpecimen.objects.get(pk=specimen.pk).remarks == remarks


def test_staff_user_can_delete_specimen(staffapp, specimen):
    assert BookSpecimen.objects.count() == 1
    assert Book.objects.count() == 1
    url = reverse('library:specimen_delete', kwargs={'pk': specimen.pk})
    form = staffapp.get(url).forms['delete_form']
    form.submit()
    assert Book.objects.count() == 1
    assert not BookSpecimen.objects.count()


def test_it_should_be_possible_to_create_several_books_without_isbn(staffapp):
    assert not Book.objects.count()
    url = reverse('library:book_create')
    form = staffapp.get(url).forms['model_form']
    form['title'] = 'My book title'
    form['summary'] = 'My book summary'
    form['section'] = '1'
    form['isbn'] = ''
    form.submit().follow()
    form = staffapp.get(url).forms['model_form']
    form['title'] = 'My book title 2'
    form['summary'] = 'My book summary 2'
    form['section'] = '2'
    form['isbn'] = ''
    form.submit().follow()
    assert Book.objects.count() == 2


def test_it_should_be_possible_to_remove_isbn_from_books(staffapp):
    book1 = BookFactory(isbn='123456')
    book2 = BookFactory(isbn='321564987')
    assert not Book.objects.filter(isbn__isnull=True)
    form = staffapp.get(reverse('library:book_update',
                        kwargs={'pk': book1.pk})).forms['model_form']
    form['isbn'] = ''
    form.submit().follow()
    form = staffapp.get(reverse('library:book_update',
                        kwargs={'pk': book2.pk})).forms['model_form']
    form['isbn'] = ''
    form.submit().follow()
    assert len(Book.objects.filter(isbn__isnull=True)) == 2


def test_should_keep_only_numbers_in_isbn(staffapp):
    form = staffapp.get(reverse('library:book_create')).forms['model_form']
    assert not Book.objects.count()
    form['title'] = 'My book title'
    form['summary'] = 'My book summary'
    form['section'] = '1'
    form['isbn'] = '2-7071-2402-8'
    form.submit().follow()
    assert Book.objects.get(isbn='2707124028')


def test_import_from_isbn(staffapp, monkeypatch):
    doc = """{"ISBN:2070379043": {"publishers": [{"name": "Gallimard"}], "identifiers": {"isbn_13": ["9782070379040"], "openlibrary": ["OL8838456M"], "isbn_10": ["2070379043"], "goodreads": ["118988"], "librarything": ["1655982"]}, "weight": "7 ounces", "title": "Les Enchanteurs", "url": "https://openlibrary.org/books/OL8838456M/Les_enchanteurs", "number_of_pages": 373, "cover": {"small": "https://covers.openlibrary.org/b/id/967767-S.jpg", "large": "https://covers.openlibrary.org/b/id/967767-L.jpg", "medium": "https://covers.openlibrary.org/b/id/967767-M.jpg"}, "publish_date": "January 22, 1988", "key": "/books/OL8838456M", "authors": [{"url": "https://openlibrary.org/authors/OL123692A/Romain_Gary", "name": "Romain Gary"}]}}"""  # noqa
    monkeypatch.setattr('ideasbox.library.utils.load_cover_from_url',
                        lambda x: 'xxx')
    monkeypatch.setattr('ideasbox.library.utils.read_url', lambda x: doc)
    form = staffapp.get(reverse('library:book_import')).forms['import']
    form['from_isbn'] = '2070379043'
    response = form.submit()
    response.follow()
    assert Book.objects.count() == 1
    book = Book.objects.last()
    # Only one notice processed, we should have been redirected to its page.
    assert response.location.endswith(book.get_absolute_url())


def test_import_from_files(staffapp, monkeypatch):
    monkeypatch.setattr('ideasbox.library.utils.read_url', lambda x: None)
    form = staffapp.get(reverse('library:book_import')).forms['import']
    form['from_files'] = Upload('ideasbox/library/tests/data/moccam.csv')
    response = form.submit()
    response.follow()
    assert Book.objects.count() == 2


def test_import_from_files_does_not_duplicate(staffapp, monkeypatch):
    monkeypatch.setattr('ideasbox.library.utils.read_url', lambda x: None)
    path = 'ideasbox/library/tests/data/moccam.csv'
    with open(path) as f:
        isbn = f.read().split('\t')[0]
    # Create a book with same isbn as first entry of CSV.
    BookFactory(isbn=isbn)
    form = staffapp.get(reverse('library:book_import')).forms['import']
    form['from_files'] = Upload(path)
    response = form.submit()
    response.follow()
    assert Book.objects.count() == 2


def test_import_from_files_load_cover_if_exists(staffapp, monkeypatch):
    assert Book.objects.count() == 0
    image = 'ideasbox/tests/data/the-prophet.jpg'
    monkeypatch.setattr(
        'ideasbox.library.utils.read_url',
        lambda x: open(image).read()
    )
    form = staffapp.get(reverse('library:book_import')).forms['import']
    form['from_files'] = Upload('ideasbox/library/tests/data/moccam.csv')
    response = form.submit()
    response.follow()
    assert Book.objects.count() == 2
    assert Book.objects.last().cover
    assert open(Book.objects.last().cover.path).read() == open(image).read()


def test_by_tag_page_should_be_filtered_by_tag(app):
    plane = BookSpecimenFactory(book__tags=['plane'])
    boat = BookSpecimenFactory(book__tags=['boat'])
    response = app.get(reverse('library:by_tag', kwargs={'tag': 'plane'}))
    assert plane.book.title in response.content
    assert boat.book.title not in response.content


def test_by_tag_page_is_paginated(app, monkeypatch):
    monkeypatch.setattr(ByTag, 'paginate_by', 2)
    BookSpecimenFactory.create_batch(size=4, book__tags=['plane'])
    url = reverse('library:by_tag', kwargs={'tag': 'plane'})
    response = app.get(url)
    assert response.pyquery.find('.pagination')
    assert response.pyquery.find('.next')
    assert not response.pyquery.find('.previous')
    response = app.get(url + '?page=2')
    assert response.pyquery.find('.pagination')
    assert not response.pyquery.find('.next')
    assert response.pyquery.find('.previous')
    response = app.get(url + '?page=3', status=404)
