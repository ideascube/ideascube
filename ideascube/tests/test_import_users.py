import pytest

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from webtest import Upload

from .factories import UserFactory

pytestmark = pytest.mark.django_db
User = get_user_model()


def test_anonymous_user_should_not_access_import_users_page(app):
    response = app.get(reverse('user_import'), status=302)
    assert 'login' in response['Location']


def test_normal_user_should_not_access_import_users_page(loggedapp, user):
    response = loggedapp.get(reverse('user_import'), status=302)
    assert 'login' in response['Location']


def test_staff_should_access_import_users_page(staffapp):
    assert staffapp.get(reverse('user_import'), status=200)


def test_should_create_users(staffapp, monkeypatch):
    data = (b'serial,full_name\n'
            b'12345,Gabriel Garcia Marquez\n'
            b'23456,Miguel de Cervantes')
    form = staffapp.get(reverse('user_import')).forms['import']
    form['source'] = Upload('users.csv', data, 'text/csv')
    response = form.submit()
    response = response.follow()
    assert User.objects.count() == 3  # Two users created plus the staff user.
    response.mustcontain('Successfully processed 2 users.')
    user = User.objects.order_by('pk')[1]
    assert user.serial == '12345'
    assert user.full_name == 'Gabriel Garcia Marquez'
    user = User.objects.order_by('pk')[2]
    assert user.serial == '23456'
    assert user.full_name == 'Miguel de Cervantes'


def test_does_not_fail_on_unknown_column(staffapp, monkeypatch):
    data = (b'serial,full_name,unknown\n'
            b'12345,Gabriel Garcia Marquez,xxxx')
    form = staffapp.get(reverse('user_import')).forms['import']
    form['source'] = Upload('users.csv', data, 'text/csv')
    response = form.submit()
    response.follow()
    assert User.objects.count() == 2
    user = User.objects.order_by('pk').last()
    assert user.serial == '12345'
    assert user.full_name == 'Gabriel Garcia Marquez'


def test_does_not_fail_on_readonly_column(staffapp, monkeypatch):
    data = (b'serial,full_name,created_at\n'
            b'12345,Gabriel Garcia Marquez,2016-10-04 09:07:23.443699+00:00')
    form = staffapp.get(reverse('user_import')).forms['import']
    form['source'] = Upload('users.csv', data, 'text/csv')
    response = form.submit()
    response.follow()
    assert User.objects.count() == 2
    user = User.objects.order_by('pk').last()
    assert user.serial == '12345'
    assert user.full_name == 'Gabriel Garcia Marquez'


def test_does_not_import_without_serial(staffapp, monkeypatch):
    data = (b'full_name\n'
            b'Gabriel Garcia Marquez')
    form = staffapp.get(reverse('user_import')).forms['import']
    form['source'] = Upload('users.csv', data, 'text/csv')
    response = form.submit()
    response.follow()
    assert User.objects.count() == 1  # The staff user only.


def test_does_not_import_with_empty_serial(staffapp, monkeypatch):
    data = (b'serial,full_name\n'
            b',Gabriel Garcia Marquez')
    form = staffapp.get(reverse('user_import')).forms['import']
    form['source'] = Upload('users.csv', data, 'text/csv')
    response = form.submit()
    response.follow()
    assert User.objects.count() == 1  # The staff user only.


def test_does_not_import_if_form_is_invalid(staffapp, monkeypatch):
    data = (b'serial,full_name,school_level\n'
            b'12345,Gabriel Garcia Marquez,invalid')
    form = staffapp.get(reverse('user_import')).forms['import']
    form['source'] = Upload('users.csv', data, 'text/csv')
    response = form.submit()
    response = response.follow()
    response.mustcontain('Invalid row at line 1')
    assert User.objects.count() == 1  # The staff user only.


def test_should_import_arabic(staffapp, monkeypatch):
    data = ('serial,full_name\n'
            '12345,جبران خليل جبران')
    form = staffapp.get(reverse('user_import')).forms['import']
    form['source'] = Upload('users.csv', data.encode(), 'text/csv')
    response = form.submit()
    response.follow()
    assert User.objects.count() == 2
    user = User.objects.order_by('pk').last()
    assert user.serial == '12345'
    assert user.full_name == 'جبران خليل جبران'


def test_should_import_boolean(staffapp, monkeypatch):
    # True/False is how we do export the data, so let's accept this in input
    # too.
    data = (b'serial,full_name,is_sent_to_school\n'
            b'12345,Gabriel Garcia Marquez,True\n'
            b'23456,Miguel de Cervantes,False')
    form = staffapp.get(reverse('user_import')).forms['import']
    form['source'] = Upload('users.csv', data, 'text/csv')
    response = form.submit()
    response.follow()
    assert User.objects.count() == 3
    user = User.objects.order_by('pk')[1]
    assert user.serial == '12345'
    assert user.is_sent_to_school is True
    user = User.objects.order_by('pk')[2]
    assert user.serial == '23456'
    assert user.is_sent_to_school is False


def test_should_import_date(staffapp, monkeypatch):
    data = (b'serial,full_name,camp_entry_date\n'
            b'12345,Gabriel Garcia Marquez,2016-10-27')
    form = staffapp.get(reverse('user_import')).forms['import']
    form['source'] = Upload('users.csv', data, 'text/csv')
    response = form.submit()
    response.follow()
    assert User.objects.count() == 2
    user = User.objects.order_by('pk').last()
    assert user.serial == '12345'
    assert user.camp_entry_date.year == 2016
    assert user.camp_entry_date.month == 10
    assert user.camp_entry_date.day == 27


def test_should_update_existing_users(staffapp, monkeypatch):
    data = (b'serial,full_name\n'
            b'12345,Gabriel Garcia Marquez')
    UserFactory(full_name='Gabriel Garcia Marques', serial='12345')
    assert User.objects.count() == 2
    form = staffapp.get(reverse('user_import')).forms['import']
    form['source'] = Upload('users.csv', data, 'text/csv')
    response = form.submit()
    response.follow()
    assert User.objects.count() == 2
    user = User.objects.order_by('pk').last()
    assert user.serial == '12345'
    assert user.full_name == 'Gabriel Garcia Marquez'  # s has been fixed in z.


def test_should_not_replace_is_staff(staffapp, monkeypatch):
    data = (b'serial,full_name,is_staff\n'
            b'12345,Gabriel Garcia Marquez,True\n'
            b'23456,Miguel de Cervantes,False')
    UserFactory(serial='12345', is_staff=False)
    UserFactory(serial='23456', is_staff=True)
    form = staffapp.get(reverse('user_import')).forms['import']
    form['source'] = Upload('users.csv', data, 'text/csv')
    response = form.submit()
    response.follow()
    user = User.objects.order_by('pk')[1]
    assert user.serial == '12345'
    assert user.full_name == 'Gabriel Garcia Marquez'
    assert user.is_staff is False
    user = User.objects.order_by('pk')[2]
    assert user.is_staff is True
    assert user.full_name == 'Miguel de Cervantes'


def test_should_not_set_password(staffapp, monkeypatch):
    data = (b'serial,full_name,password\n'
            b'12345,Gabriel Garcia Marquez,123456')
    form = staffapp.get(reverse('user_import')).forms['import']
    form['source'] = Upload('users.csv', data, 'text/csv')
    response = form.submit()
    response.follow()
    user = User.objects.order_by('pk')[1]
    assert user.serial == '12345'
    assert user.full_name == 'Gabriel Garcia Marquez'
    assert not user.password


def test_should_not_change_password(staffapp, monkeypatch):
    data = (b'serial,full_name,password\n'
            b'12345,Gabriel Garcia Marquez,123456')
    before = UserFactory(serial='12345', is_staff=False)
    form = staffapp.get(reverse('user_import')).forms['import']
    form['source'] = Upload('users.csv', data, 'text/csv')
    response = form.submit()
    response.follow()
    user = User.objects.order_by('pk')[1]
    assert user.serial == '12345'
    assert user.full_name == 'Gabriel Garcia Marquez'
    assert user.password == before.password


@pytest.mark.usefixtures('systemuser')
def test_does_not_try_to_create_system_user(staffapp, monkeypatch):
    qs = User.objects.get_queryset_unfiltered()
    assert qs.count() == 2
    data = (b'serial,full_name,unknown\n'
            b'__system__,ANewFunkyName,xxxx')
    form = staffapp.get(reverse('user_import')).forms['import']
    form['source'] = Upload('users.csv', data, 'text/csv')
    response = form.submit()
    response.follow()
    assert qs.count() == 2
    user = qs.get(serial='__system__')
    assert user.full_name != 'ANewFunkyName'
