import pytest
from django.core.urlresolvers import reverse


from ideascube.library.tests.factories import BookFactory, BookSpecimenFactory

pytestmark = pytest.mark.django_db


def test_book_appears_in_the_stock_list_if_it_has_physical_specimen(staffapp):
    specimen = BookSpecimenFactory(barcode='1928323', item__name='Cerf-Volant')
    resp = staffapp.get(reverse('monitoring:stock'), status=200)
    resp.mustcontain(specimen.item.name, specimen.barcode, 'Total: 1')


def test_book_without_specimen_does_not_appear_in_the_stock_list(staffapp):
    book = BookFactory(name='Cerf-Volant')
    resp = staffapp.get(reverse('monitoring:stock'), status=200)
    resp.mustcontain(no=book.name)


def test_book_with_only_digital_specimen_does_not_appear(staffapp):
    specimen = BookSpecimenFactory(is_digital=True)
    resp = staffapp.get(reverse('monitoring:stock'), status=200)
    resp.mustcontain(no=['Total: 1', specimen.item.name])


def test_book_with_both_specimen_appears_not_the_digital_specimen(staffapp):
    digital = BookSpecimenFactory(is_digital=True)
    physical = BookSpecimenFactory(item=digital.item, barcode='12345')
    resp = staffapp.get(reverse('monitoring:stock'), status=200)
    resp.mustcontain('Total: 1', physical.item.name, physical.barcode)
