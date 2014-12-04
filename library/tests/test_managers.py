import pytest

from ..models import Book

pytestmark = pytest.mark.django_db


def test_available_should_return_only_book_with_specimen(book, specimen):
    books = Book.available.all()
    assert specimen.book in books
    assert book not in books


def test_objects_should_return_all_books(book, specimen):
    books = Book.objects.all()
    assert specimen.book in books
    assert book in books
