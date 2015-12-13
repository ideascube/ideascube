# -*- coding: utf-8 -*-
from datetime import date, timedelta

import pytest
from django.core.urlresolvers import reverse
from django.utils import translation

from ideascube.tests.factories import UserFactory

from ..models import (Entry, Inventory, InventorySpecimen, Loan, Specimen,
                      StockItem)
from .factories import (EntryFactory, InventoryFactory, LoanFactory,
                        SpecimenFactory, StockItemFactory)

pytestmark = pytest.mark.django_db


def test_anonymous_should_not_access_entry_page(app):
    assert app.get(reverse('monitoring:entry'), status=302)


def test_non_staff_should_not_access_entry_page(loggedapp):
    assert loggedapp.get(reverse('monitoring:entry'), status=302)


def test_staff_should_access_entry_page(staffapp):
    assert staffapp.get(reverse('monitoring:entry'), status=200)


@pytest.mark.parametrize('module', [m[0] for m in Entry.MODULES])
def test_can_create_entries(module, staffapp):
    UserFactory(serial='123456')
    assert not Entry.objects.count()
    form = staffapp.get(reverse('monitoring:entry')).forms['entry_form']
    form['serials'] = '123456'
    form.submit('entry_' + module).follow()
    assert Entry.objects.count()


def test_cannot_create_entries_with_duplicate_serials(staffapp):
    UserFactory(serial='123456')
    assert not Entry.objects.count()
    form = staffapp.get(reverse('monitoring:entry')).forms['entry_form']
    form['serials'] = '123456\n123456'
    form.submit('entry_cinema').follow()
    assert Entry.objects.count() == 1


def test_can_create_entries_with_activity(staffapp):
    UserFactory(serial='123456')
    form = staffapp.get(reverse('monitoring:entry')).forms['entry_form']
    form['serials'] = '123456'
    form['activity'] = 'special activity'
    form.submit('entry_cinema').follow()
    Entry.objects.last().activity == 'special activity'


def test_anonymous_should_not_access_export_entry_url(app):
    assert app.get(reverse('monitoring:export_entry'), status=302)


def test_non_staff_should_not_access_export_entry_url(loggedapp):
    assert loggedapp.get(reverse('monitoring:export_entry'), status=302)


def test_staff_should_access_export_entry_url(staffapp):
    assert staffapp.get(reverse('monitoring:export_entry'), status=200)


def test_export_entry_should_return_csv_with_entries(staffapp, settings):
    EntryFactory.create_batch(3)
    settings.MONITORING_ENTRY_EXPORT_FIELDS = []
    resp = staffapp.get(reverse('monitoring:export_entry'), status=200)
    assert resp.content.startswith("module,date,activity,partner\r\ncinema,")
    assert resp.content.count("cinema") == 3


def test_anonymous_should_not_access_stock_page(app):
    assert app.get(reverse('monitoring:stock'), status=302)


def test_non_staff_should_not_access_stock_page(loggedapp):
    assert loggedapp.get(reverse('monitoring:stock'), status=302)


def test_staff_should_access_stock_page(staffapp):
    assert staffapp.get(reverse('monitoring:stock'), status=200)


def test_anonymous_should_not_access_stockitem_create_page(app):
    assert app.get(reverse('monitoring:stockitem_create'), status=302)


def test_non_staff_should_not_access_stockitem_create_page(loggedapp):
    assert loggedapp.get(reverse('monitoring:stockitem_create'), status=302)


def test_staff_should_access_stockitem_create_page(staffapp):
    assert staffapp.get(reverse('monitoring:stockitem_create'), status=200)


def test_staff_can_create_stockitem(staffapp):
    url = reverse('monitoring:stockitem_create')
    form = staffapp.get(url).forms['model_form']
    assert not StockItem.objects.count()
    form['module'] = StockItem.LIBRARY
    form['name'] = 'My stock item'
    form.submit().follow()
    assert StockItem.objects.count()


def test_stockitem_create_view_should_accept_module_parameter(staffapp):
    url = '{}?module={}'.format(reverse('monitoring:stockitem_create'),
                                StockItem.CINEMA)
    form = staffapp.get(url).forms['model_form']
    assert form['module'].value == StockItem.CINEMA


def test_staff_can_update_stockitem(staffapp):
    item = StockItemFactory(module=StockItem.DIGITAL)
    url = reverse('monitoring:stockitem_update', kwargs={'pk': item.pk})
    form = staffapp.get(url).forms['model_form']
    form['module'] = StockItem.LIBRARY
    form.submit().follow()
    assert StockItem.objects.get(pk=item.pk).module == StockItem.LIBRARY


def test_staff_can_create_specimen(staffapp):
    item = StockItemFactory()
    url = reverse('monitoring:specimen_create', kwargs={'item_pk': item.pk})
    form = staffapp.get(url).forms['model_form']
    assert not item.specimens.count()
    form['barcode'] = '23135321'
    form.submit().follow()
    assert item.specimens.count()


def test_staff_can_create_specimen_with_letters_and_ints_in_barcode(staffapp):
    item = StockItemFactory()
    url = reverse('monitoring:specimen_create', kwargs={'item_pk': item.pk})
    form = staffapp.get(url).forms['model_form']
    assert not item.specimens.count()
    form['barcode'] = '123abc'
    form.submit().follow()
    assert item.specimens.filter(barcode='123abc').count()


def test_staff_can_edit_specimen(staffapp):
    specimen = SpecimenFactory(count=3)
    url = reverse('monitoring:specimen_update', kwargs={'pk': specimen.pk})
    form = staffapp.get(url).forms['model_form']
    form['count'] == 3
    form['count'] = 4
    form.submit().follow()
    assert Specimen.objects.get(pk=specimen.pk).count == 4


def test_anonymous_should_not_access_inventory_create_page(app):
    assert app.get(reverse('monitoring:inventory_create'), status=302)


def test_non_staff_should_not_access_inventory_create_page(loggedapp):
    assert loggedapp.get(reverse('monitoring:inventory_create'), status=302)


def test_staff_should_access_inventory_create_page(staffapp):
    assert staffapp.get(reverse('monitoring:inventory_create'), status=200)


def test_staff_can_create_inventory(staffapp):
    url = reverse('monitoring:inventory_create')
    form = staffapp.get(url).forms['model_form']
    assert not Inventory.objects.count()
    form['made_at'] = '2015-03-22'
    form.submit().follow()
    assert Inventory.objects.count()


def test_staff_can_update_inventory(staffapp):
    inventory = InventoryFactory()
    url = reverse('monitoring:inventory_update', kwargs={'pk': inventory.pk})
    form = staffapp.get(url).forms['model_form']
    comments = 'A new comment'
    form['comments'] = comments
    form.submit().follow()
    assert Inventory.objects.get(pk=inventory.pk).comments == comments


def test_anonymous_should_not_access_inventory_detail_page(app):
    inventory = InventoryFactory()
    url = reverse('monitoring:inventory', kwargs={'pk': inventory.pk})
    assert app.get(url, status=302)


def test_non_staff_should_not_access_inventory_detail_page(loggedapp):
    inventory = InventoryFactory()
    url = reverse('monitoring:inventory', kwargs={'pk': inventory.pk})
    assert loggedapp.get(url, status=302)


def test_staff_should_access_inventory_detail_page(staffapp):
    inventory = InventoryFactory()
    url = reverse('monitoring:inventory', kwargs={'pk': inventory.pk})
    assert staffapp.get(url, status=200)


def test_can_export_inventory(staffapp):
    inventory = InventoryFactory()
    specimen = SpecimenFactory(item__name="an item")
    InventorySpecimen.objects.create(inventory=inventory, specimen=specimen)
    url = reverse('monitoring:inventory_export', kwargs={'pk': inventory.pk})
    resp = staffapp.get(url, status=200)
    assert resp.content.startswith("module,name,description,barcode,serial,count,comments,status\r\ncinema,an item")  # noqa


def test_export_inventory_should_be_ok_in_arabic(staffapp, settings):
    translation.activate('ar')
    inventory = InventoryFactory()
    specimen = SpecimenFactory(item__name="an item", comments=u"النبي (كتاب)")
    InventorySpecimen.objects.create(inventory=inventory, specimen=specimen)
    url = reverse('monitoring:inventory_export', kwargs={'pk': inventory.pk})
    resp = staffapp.get(url, status=200)
    resp.mustcontain(specimen.comments)
    translation.deactivate()


def test_staff_can_create_inventoryspeciment_by_barcode(staffapp):
    inventory = InventoryFactory()
    specimen = SpecimenFactory()
    assert not InventorySpecimen.objects.filter(inventory=inventory,
                                                specimen=specimen)
    url = reverse('monitoring:inventory', kwargs={'pk': inventory.pk})
    form = staffapp.get(url).forms['by_barcode']
    form['specimen'] = specimen.barcode
    form.submit().follow()
    assert InventorySpecimen.objects.get(inventory=inventory,
                                         specimen=specimen)


def test_cant_create_inventoryspeciment_by_barcode_twice(staffapp):
    inventory = InventoryFactory()
    specimen = SpecimenFactory()
    assert not InventorySpecimen.objects.filter(inventory=inventory,
                                                specimen=specimen)
    url = reverse('monitoring:inventory', kwargs={'pk': inventory.pk})
    form = staffapp.get(url).forms['by_barcode']
    form['specimen'] = specimen.barcode
    form.submit().follow()
    form = staffapp.get(url).forms['by_barcode']
    form['specimen'] = specimen.barcode
    form.submit().follow()
    assert InventorySpecimen.objects.filter(inventory=inventory,
                                            specimen=specimen).count() == 1


def test_staff_can_create_inventoryspeciment_by_click_on_add_link(staffapp):
    inventory = InventoryFactory()
    specimen = SpecimenFactory(count=3)
    assert not InventorySpecimen.objects.filter(inventory=inventory,
                                                specimen=specimen)
    url = reverse('monitoring:inventory', kwargs={'pk': inventory.pk})
    resp = staffapp.get(url)
    redirect = resp.click(href=reverse('monitoring:inventoryspecimen_add',
                                       kwargs={
                                            'inventory_pk': inventory.pk,
                                            'specimen_pk': specimen.pk}))
    assert redirect.location.endswith(url)
    assert InventorySpecimen.objects.get(inventory=inventory,
                                         specimen=specimen)
    assert InventorySpecimen.objects.get(inventory=inventory,
                                         specimen=specimen).count == 3


def test_staff_can_remove_inventoryspeciment_by_click_on_remove_link(staffapp):
    inventory = InventoryFactory()
    specimen = SpecimenFactory()
    InventorySpecimen.objects.create(inventory=inventory,
                                     specimen=specimen)
    url = reverse('monitoring:inventory', kwargs={'pk': inventory.pk})
    resp = staffapp.get(url)
    redirect = resp.click(href=reverse('monitoring:inventoryspecimen_remove',
                                       kwargs={
                                            'inventory_pk': inventory.pk,
                                            'specimen_pk': specimen.pk}))
    assert redirect.location.endswith(url)
    assert not InventorySpecimen.objects.filter(inventory=inventory,
                                                specimen=specimen)


def test_can_increase_inventoryspeciment_by_click_on_increase_link(staffapp):
    inventory = InventoryFactory()
    specimen = SpecimenFactory()
    m2m = InventorySpecimen.objects.create(inventory=inventory,
                                           specimen=specimen,
                                           count=2)
    url = reverse('monitoring:inventory', kwargs={'pk': inventory.pk})
    resp = staffapp.get(url)
    redirect = resp.click(href=reverse('monitoring:inventoryspecimen_increase',
                                       kwargs={'pk': m2m.pk}))
    assert redirect.location.endswith(url)
    assert InventorySpecimen.objects.get(inventory=inventory,
                                         specimen=specimen).count == 3


def test_can_decrease_inventoryspeciment_by_click_on_decrease_link(staffapp):
    inventory = InventoryFactory()
    specimen = SpecimenFactory()
    m2m = InventorySpecimen.objects.create(inventory=inventory,
                                           specimen=specimen,
                                           count=2)
    url = reverse('monitoring:inventory', kwargs={'pk': inventory.pk})
    resp = staffapp.get(url)
    redirect = resp.click(href=reverse('monitoring:inventoryspecimen_decrease',
                                       kwargs={'pk': m2m.pk}))
    assert redirect.location.endswith(url)
    assert InventorySpecimen.objects.get(inventory=inventory,
                                         specimen=specimen).count == 1


def test_can_loan(staffapp, user):
    assert not Loan.objects.count()
    specimen = SpecimenFactory()
    url = reverse('monitoring:loan')
    form = staffapp.get(url).forms['loan_form']
    form['specimen'] = specimen.barcode
    form['user'] = user.serial
    form.submit('do_loan')
    assert Loan.objects.count() == 1


def test_default_loan_duration_can_be_changed(staffapp, settings):
    settings.LOAN_DURATION = 7
    url = reverse('monitoring:loan')
    form = staffapp.get(url).forms['loan_form']
    due_date = (date.today() + timedelta(days=7)).isoformat()
    assert form['due_date'].value == due_date


def test_cannot_loan_twice_same_item(staffapp, user):
    assert not Loan.objects.count()
    specimen = SpecimenFactory()
    url = reverse('monitoring:loan')
    form = staffapp.get(url).forms['loan_form']
    form['specimen'] = specimen.barcode
    form['user'] = user.serial
    form.submit('do_loan')
    assert Loan.objects.due().count() == 1
    form = staffapp.get(url).forms['loan_form']
    form['specimen'] = specimen.barcode
    form['user'] = staffapp.user.serial
    form.submit('do_loan')
    assert Loan.objects.due().count() == 1


def test_can_loan_twice_same_item_when_first_is_returned(staffapp, user):
    assert not Loan.objects.count()
    specimen = SpecimenFactory()
    url = reverse('monitoring:loan')
    form = staffapp.get(url).forms['loan_form']
    form['specimen'] = specimen.barcode
    form['user'] = user.serial
    form.submit('do_loan')
    assert Loan.objects.due().count() == 1

    # Return it.
    form = staffapp.get(url).forms['return_form']
    form['loan'] = specimen.barcode
    form.submit('do_return')
    assert Loan.objects.due().count() == 0

    # Loan again same item.
    form = staffapp.get(url).forms['loan_form']
    form['specimen'] = specimen.barcode
    form['user'] = staffapp.user.serial
    form.submit('do_loan')
    assert Loan.objects.due().count() == 1


def test_can_return_loan(staffapp, user):
    specimen = SpecimenFactory()
    Loan.objects.create(user=user, specimen=specimen,
                        by=staffapp.user)
    assert Loan.objects.due().count() == 1
    url = reverse('monitoring:loan')
    form = staffapp.get(url).forms['return_form']
    form['loan'] = specimen.barcode
    form.submit('do_return')
    assert not Loan.objects.due().count()


def test_return_unknown_id_does_not_fail(staffapp):
    url = reverse('monitoring:loan')
    form = staffapp.get(url).forms['return_form']
    form['loan'] = '123456'
    form.submit('do_return', status=200)


def test_can_export_loan(staffapp):
    specimen = SpecimenFactory(item__name="an item", barcode="123")
    LoanFactory(specimen=specimen)
    url = reverse('monitoring:export_loan')
    resp = staffapp.get(url, status=200)
    assert resp.content.startswith("item,barcode,user,loaned at,due date,returned at,comments\r\nan item,123")  # noqa


def test_export_loan_should_be_ok_in_arabic(staffapp):
    translation.activate('ar')
    specimen = SpecimenFactory(item__name="an item", barcode="123")
    loan = LoanFactory(specimen=specimen, comments=u"النبي (كتاب)")
    url = reverse('monitoring:export_loan')
    resp = staffapp.get(url, status=200)
    assert resp.content.startswith("item,barcode,user,loaned at,due date,returned at,comments\r\nan item,123")  # noqa
    resp.mustcontain(loan.comments)
    translation.deactivate()
