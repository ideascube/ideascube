import pytest

from .factories import EntryFactory

pytestmark = pytest.mark.django_db


def test_it_should_create_an_entry_from_factory():
    entry = EntryFactory()
    assert entry.pk is not None
    assert entry.module is not None
    assert entry.user is not None


def test_it_should_override_fields_passed_to_factory():
    entry = EntryFactory()
    assert entry.module == "cinema"
    another = EntryFactory(module="library")
    assert another.module == "library"
