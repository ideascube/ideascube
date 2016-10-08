import pytest

from .factories import (BookFactory, BookSpecimenFactory,
                        DigitalBookSpecimenFactory)

pytestmark = pytest.mark.django_db


def test_it_should_create_a_default_book_from_factory():
    book = BookFactory()
    assert book.pk is not None
    assert str(book)


def test_it_should_override_book_fields_passed_to_factory():
    book = BookFactory()
    assert book.name.startswith('Test book')
    another = BookFactory(name="My custom title")
    assert another.name == "My custom title"


def test_it_should_create_a_default_book_specimen_from_factory():
    specimen = BookSpecimenFactory()
    assert specimen.pk is not None
    assert specimen.item.pk is not None
    assert str(specimen)


def test_it_should_override_specimen_fields_passed_to_factory():
    book = BookFactory()
    specimen = BookSpecimenFactory(item=book)
    assert specimen.item == book


def test_it_should_create_a_default_book_digital_specimen_from_factory():
    digitalspecimen = DigitalBookSpecimenFactory()
    assert digitalspecimen.pk is not None
    assert digitalspecimen.item.pk is not None
    assert digitalspecimen.file is not None
    assert str(digitalspecimen)
