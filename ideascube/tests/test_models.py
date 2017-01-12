import pytest

from django.contrib.auth import get_user_model

from ..models import User
from .factories import UserFactory

pytestmark = pytest.mark.django_db


def test_get_short_name_should_return_short_name():
    user = UserFactory.build()
    assert user.get_short_name() == "Sankara"


def test_get_full_name_should_return_full_name():
    user = UserFactory.build()
    assert user.get_full_name() == "Thomas Sankara"


def test_create_user():
    model = get_user_model()
    user = model.objects.create_user('123456')
    assert user.pk is not None
    assert user.serial == '123456'


def test_create_superuser():
    model = get_user_model()
    user = model.objects.create_superuser('123456', 'passw0rd')
    assert user.pk is not None
    assert user.serial == '123456'
    assert user.is_staff


def test_list_users(user, systemuser):
    model = get_user_model()
    users = model.objects.all()
    assert [u.serial for u in users] == ['123456']

    users = model.objects.get_queryset_unfiltered()
    assert sorted([u.serial for u in users]) == sorted(['__system__', '123456'])

    systemuser = model.objects.get_system_user()
    assert systemuser.serial == '__system__'


def test_client_login(client, user):
    assert client.login(serial=user.serial, password='password')


def test_user_data_fields_should_return_labels_and_values(settings):
    settings.USER_DATA_FIELDS = ['short_name', 'ar_level']

    user = User(short_name='my name', ar_level=['u', 's'])
    fields = user.data_fields
    assert 'is_staff' not in fields
    assert str(fields['short_name']['value']) == 'my name'
    assert str(fields['short_name']['label']) == 'usual name'
    assert str(fields['ar_level']['value']) == 'Understood, Spoken'
    assert str(fields['ar_level']['label']) == 'Arabic knowledge'

