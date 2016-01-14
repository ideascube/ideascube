import pytest
from django.db import IntegrityError

from ..models import Book, BookSpecimen
from .factories import BookFactory, BookSpecimenFactory

from factory.fuzzy import FuzzyText

pytestmark = pytest.mark.django_db


def test_deleting_book_sould_delete_specimen_too(specimen):
    assert BookSpecimen.objects.count()
    assert Book.objects.count()
    specimen.book.delete()
    assert not BookSpecimen.objects.count()
    assert not Book.objects.count()


def test_deleting_specimen_sould_not_delete_book(specimen):
    assert BookSpecimen.objects.count()
    assert Book.objects.count()
    specimen.delete()
    assert not BookSpecimen.objects.count()
    assert Book.objects.count()


def test_it_should_be_possible_to_have_more_than_one_isbn_null_value():
    assert len(Book.objects.filter(isbn__isnull=True)) == 0
    BookFactory(isbn=None)
    BookFactory(isbn=None)
    assert len(Book.objects.filter(isbn__isnull=True)) == 2


def test_it_should_not_be_possible_to_have_twice_the_same_isbn():
    assert len(Book.objects.filter(isbn__isnull=True)) == 0
    BookFactory(isbn='123456')
    with pytest.raises(IntegrityError):
        BookFactory(isbn='123456')


def test_can_search_books_by_tags():
    BookFactory(tags=['jordan', 'dead sea'])
    assert Book.objects.search("jordan")


def test_it_should_be_allowed_to_create_more_than_one_digital_specimen():
    BookSpecimenFactory(is_digital=True)
    BookSpecimenFactory(is_digital=True)
    assert BookSpecimen.objects.count() == 2


def test_deleting_digital_specimen():
    specimen1 = BookSpecimenFactory()
    assert BookSpecimen.objects.count()
    assert Book.objects.count()
    specimen1.delete()
    assert not BookSpecimen.objects.count()
    assert Book.objects.count()


def test_is_digital_from_model_method():
    specimen = BookSpecimenFactory(is_digital=True)
    assert specimen.is_digital


def test_is_digital_after_filling_serial_whithout_removing_file():
    specimen = BookSpecimenFactory(serial=FuzzyText(length=6), is_digital=True)
    assert specimen.is_digital


def test_is_not_digital_after_removing_file():
    specimen = BookSpecimenFactory(file=None)
    assert not specimen.is_digital


def test_unicode_returns_digital_specimen_of_book():
    book = BookFactory()
    specimen = BookSpecimenFactory(book=book, is_digital=True)
    assert str(specimen).startswith(u'Digital specimen of')
