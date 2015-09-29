import pytest

from .factories import (EntryFactory, InventoryFactory, LoanFactory,
                        SpecimenFactory, StockItemFactory)

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


def test_it_should_create_an_inventory_from_factory():
    inventory = InventoryFactory()
    assert inventory.pk is not None
    assert inventory.made_at is not None


def test_it_should_create_a_stockitem_from_factory():
    stockitem = StockItemFactory()
    assert stockitem.pk is not None
    assert stockitem.module is not None
    assert stockitem.name is not None


def test_it_should_override_stockitem_fields_passed_to_factory():
    stockitem = StockItemFactory()
    assert stockitem.module == "cinema"
    another = StockItemFactory(module="library")
    assert another.module == "library"


def test_it_should_create_a_default_stockitem_from_specimen_factory():
    specimen = SpecimenFactory()
    assert specimen.pk is not None
    assert specimen.item.pk is not None


def test_it_should_override_specimen_fields_passed_to_factory():
    item = StockItemFactory()
    specimen = SpecimenFactory(item=item)
    assert specimen.item == item


def test_it_should_create_a_default_loan_from_loan_factory():
    loan = LoanFactory()
    assert loan.pk is not None
    assert loan.specimen.pk is not None


def test_it_should_override_loan_fields_passed_to_factory():
    specimen = SpecimenFactory()
    loan = LoanFactory(specimen=specimen)
    assert loan.specimen == specimen
