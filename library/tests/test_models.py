import pytest

from ..models import Book, BookSpecimen

pytestmark = pytest.mark.django_db


def test_deleting_book_sould_delete_specimen_too(specimen):
    assert BookSpecimen.objects.all()
    assert Book.objects.all()
    specimen.book.delete()
    assert not BookSpecimen.objects.all()
    assert not Book.objects.all()


def test_deleting_specimen_sould_not_delete_book(specimen):
    assert BookSpecimen.objects.all()
    assert Book.objects.all()
    specimen.delete()
    assert not BookSpecimen.objects.all()
    assert Book.objects.all()
