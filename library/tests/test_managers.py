import pytest

from ..models import Book
from .factories import BookSpecimenFactory

pytestmark = pytest.mark.django_db


def test_available_should_return_only_book_with_specimen(book, specimen):
    books = Book.objects.available()
    assert specimen.book in books
    assert book not in books


def test_available_should_be_chainable(book, specimen):
    specimen1 = BookSpecimenFactory(serial='321654')
    specimen2 = BookSpecimenFactory(serial='987456')
    books = Book.objects.available().filter(specimens__serial='321654')
    assert specimen1.book in books
    assert specimen2.book not in books


def test_objects_should_return_all_books(book, specimen):
    books = Book.objects.all()
    assert specimen.book in books
    assert book in books
