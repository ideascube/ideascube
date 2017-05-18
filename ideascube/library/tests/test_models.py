import pytest
from django.db import IntegrityError
from factory.fuzzy import FuzzyText

from ..models import Book, BookSpecimen
from .factories import (BookFactory, BookSpecimenFactory,
                        DigitalBookSpecimenFactory)

pytestmark = pytest.mark.django_db


def test_deleting_book_sould_delete_specimen_too(specimen):
    assert BookSpecimen.objects.count()
    assert Book.objects.count()
    specimen.item.delete()
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
    assert Book.objects.search(text__match="jordan")


def test_it_should_be_allowed_to_create_more_than_one_digital_specimen():
    DigitalBookSpecimenFactory()
    DigitalBookSpecimenFactory()
    assert BookSpecimen.objects.count() == 2


def test_deleting_digital_specimen():
    specimen1 = BookSpecimenFactory()
    assert BookSpecimen.objects.count()
    assert Book.objects.count()
    specimen1.delete()
    assert not BookSpecimen.objects.count()
    assert Book.objects.count()


def test_physical_from_model_method():
    specimen = DigitalBookSpecimenFactory()
    assert not specimen.physical


def test_is_physical_after_filling_barcode_whithout_removing_file():
    specimen = DigitalBookSpecimenFactory(
        barcode=FuzzyText(length=6))
    assert not specimen.physical


def test_physical_after_removing_file():
    specimen = BookSpecimenFactory(file=None)
    assert specimen.physical


def test_unicode_returns_digital_specimen_of_book():
    book = BookFactory()
    specimen = DigitalBookSpecimenFactory(item=book)
    assert str(specimen).startswith('Digital specimen of')


def test_specimen_extension():
    specimen = DigitalBookSpecimenFactory(file__filename='book.epub')
    assert specimen.extension == 'epub'


def test_specimen_without_extension():
    specimen = DigitalBookSpecimenFactory(file__filename='book')
    assert specimen.extension == ''


def test_pysical_specimen_extension():
    specimen = BookSpecimenFactory()
    assert specimen.extension == ''
