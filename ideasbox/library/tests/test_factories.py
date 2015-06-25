import pytest

from .factories import BookFactory, BookSpecimenFactory

pytestmark = pytest.mark.django_db


def test_it_should_create_a_default_book_from_factory():
    book = BookFactory()
    assert book.pk is not None
    assert unicode(book)


def test_it_should_override_book_fields_passed_to_factory():
    book = BookFactory()
    assert book.title.startswith('Test book')
    another = BookFactory(title="My custom title")
    assert another.title == "My custom title"


def test_it_should_create_a_default_book_specimen_from_factory():
    specimen = BookSpecimenFactory()
    assert specimen.pk is not None
    assert specimen.book.pk is not None
    assert unicode(specimen)


def test_it_should_override_specimen_fields_passed_to_factory():
    book = BookFactory()
    specimen = BookSpecimenFactory(book=book)
    assert specimen.book == book


def test_it_should_create_a_default_book_digital_specimen_from_factory():
    digitalspecimen = BookSpecimenFactory(is_digital=True)
    assert digitalspecimen.pk is not None
    assert digitalspecimen.book.pk is not None
    assert digitalspecimen.file is not None
    assert unicode(digitalspecimen)
