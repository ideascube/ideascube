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
    data = (b'serial,full_name,birth_year\n'
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


def test_import_from_llavedelsaber_format(staffapp, settings):
    settings.USER_IMPORT_FORMATS = (
        ('llavedelsaber', 'Llave del Saber'),
        ('ideascube', 'Ideascube'),
    )

    # TODO: The format of Llave del Saber exports is not finalized
    data = '\n'.join([
        '"serial";"a_field";"another_field";"a_third_field";"last_field"',
        '"206678478";"";"";"";""',
        '"206678201";"";"";"";""',
    ])

    form = staffapp.get(reverse('user_import')).forms['import']
    form['format'] = 'llavedelsaber'
    form['source'] = Upload('users.csv', data.encode('utf-8'), 'text/csv')
    form.submit(status=302).follow(status=200)

    users = User.objects.all().order_by('serial')
    assert users.count() == 3  # The two imported, plus the staff

    # TODO: Test the other imported fields eventually
    serials = [u.serial for u in users]
    assert serials == ['123456staff', '206678201', '206678478']


def test_import_from_llavedelsaber_format_invalid_data(staffapp, settings):
    settings.USER_IMPORT_FORMATS = (
        ('llavedelsaber', 'Llave del Saber'),
        ('ideascube', 'Ideascube'),
    )

    # TODO: The format of Llave del Saber exports is not finalized
    data = '\n'.join([
        '"llave";"a_field";"another_field";"a_third_field";"last_field"',
        '"206678478";"";"";"";""',
        '"206678201";"";"";"";""',
    ])

    form = staffapp.get(reverse('user_import')).forms['import']
    form['format'] = 'llavedelsaber'
    form['source'] = Upload('users.csv', data.encode('utf-8'), 'text/csv')
    response = form.submit(status=302).follow(status=200)
    assert 'Invalid row at line 1: serial missing' in response.text
    assert 'Invalid row at line 2: serial missing' in response.text

    users = User.objects.all()
    assert users.count() == 1  # The staff


def test_import_from_invalid_format(staffapp, settings):
    settings.USER_IMPORT_FORMATS = (
        ('llavedelsaber', 'Llave del Saber'),
        ('ideascube', 'Ideascube'),
    )
    data = 'whatever, this will not be imported'

    form = staffapp.get(reverse('user_import')).forms['import']
    form['format'].force_value('no-such-format')
    form['source'] = Upload('users.csv', data.encode('utf-8'), 'text/csv')
    response = form.submit(status=200)
    assert (
        'Select a valid choice. no-such-format is not one of the available '
        'choices.') in response.text

    users = User.objects.all()
    assert users.count() == 1  # The staff
