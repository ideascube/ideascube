import pytest

from django.core.urlresolvers import reverse

from ideasbox.tests.factories import UserFactory
from ..models import Entry
from .factories import EntryFactory

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
    assert resp.content.startswith("module,date\r\ncinema,")
    assert resp.content.count("cinema") == 3
