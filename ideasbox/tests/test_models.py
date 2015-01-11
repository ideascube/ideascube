import pytest

from django.contrib.auth import get_user_model

from ..models import BurundiRefugeeUser
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


def test_client_login(client, user):
    assert client.login(serial=user.serial, password='password')


def test_user_public_fields_should_return_labels_and_values():
    user = BurundiRefugeeUser(
        short_name='my name',
        school_level=1
    )
    fields = user.public_fields
    assert 'is_staff' not in fields
    assert fields['short_name']['value'] == 'my name'
    assert fields['short_name']['label'] == 'usual name'
    assert fields['school_level']['value'] == 'Primary'
    assert fields['school_level']['label'] == 'School level'
