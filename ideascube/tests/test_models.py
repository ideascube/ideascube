from datetime import datetime, timezone

import freezegun
import pytest

from django.contrib.auth import get_user_model
from django.db import models

from ..models import JSONField, User
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


def test_user_data_fields_should_return_labels_and_values():
    user = User(short_name='my name', ar_level=['u', 's'])
    fields = user.data_fields
    assert 'is_staff' not in fields
    assert str(fields['short_name']['value']) == 'my name'
    assert str(fields['short_name']['label']) == 'usual name'
    assert str(fields['ar_level']['value']) == 'Understood, Spoken'
    assert str(fields['ar_level']['label']) == 'Arabic knowledge'


class JSONModel(models.Model):
    class Meta:
        app_label = 'ideascube'

    data = JSONField()


@pytest.mark.parametrize(
    'value',
    [
        True,
        42,
        None,
        'A string',
        [1, 2, 3],
        {'foo': 'bar'}
    ],
    ids=[
        'boolean',
        'int',
        'none',
        'string',
        'list',
        'dict',
    ])
def test_json_field(value):
    obj = JSONModel(data=value)
    obj.save()
    assert JSONModel.objects.count() == 1

    obj = JSONModel.objects.first()
    assert obj.data == value


@pytest.mark.parametrize(
    'value',
    [
        True, 42, None, 'A string', [1, '2'],
    ],
    ids=[
        'boolean', 'int', 'none', 'string', 'list',
    ])
def test_settings(value, user):
    from ideascube.models import Setting

    fakenow = datetime.now(tz=timezone.utc)
    assert Setting.objects.count() == 0

    with freezegun.freeze_time(fakenow):
        Setting(
            namespace='tests', key='setting1', value=value, actor=user).save()

    assert Setting.objects.count() == 1

    setting = Setting.objects.first()
    assert setting.namespace == 'tests'
    assert setting.key == 'setting1'
    assert setting.value == value
    assert setting.actor == user
    assert setting.date == fakenow
    assert str(setting) == 'tests.setting1=%r' % value


@pytest.mark.parametrize(
    'value1, value2',
    [
        (True, False),
        (42, 43),
        ('A string', 'Another string'),
        ([1, '2'], ['foo', None]),
    ],
    ids=[
        'boolean', 'int', 'string', 'list',
    ])
def test_set_settings(value1, value2, user):
    from ideascube.models import Setting

    fakenow = datetime.now(tz=timezone.utc)

    with freezegun.freeze_time(fakenow):
        Setting.set('tests', 'setting1', value1, user)

    assert Setting.objects.count() == 1

    setting = Setting.objects.first()
    assert setting.namespace == 'tests'
    assert setting.key == 'setting1'
    assert setting.value == value1
    assert setting.actor == user
    assert setting.date == fakenow
    assert str(setting) == 'tests.setting1=%r' % value1

    Setting.set('tests', 'setting1', value2, user)

    assert Setting.objects.count() == 1

    setting = Setting.objects.first()
    assert setting.namespace == 'tests'
    assert setting.key == 'setting1'
    assert setting.value == value2
    assert str(setting) == 'tests.setting1=%r' % value2


def test_get_string_setting(user):
    from ideascube.models import Setting

    Setting(
        namespace='tests', key='setting1', value='value1', actor=user).save()
    assert Setting.objects.count() == 1

    assert Setting.get_string('tests', 'setting1') == 'value1'


def test_get_unexistent_string_setting():
    from ideascube.models import Setting

    with pytest.raises(Setting.DoesNotExist):
        Setting.get_string('tests', 'setting1')

    assert Setting.get_string(
        'tests', 'setting1', default='the default') == 'the default'


@pytest.mark.parametrize(
    'value',
    [
        True, 42, None, [1, '2'],
    ],
    ids=[
        'boolean', 'int', 'none', 'list',
    ])
def test_get_nonstring_setting(value, user):
    from ideascube.models import Setting

    Setting(namespace='tests', key='setting1', value=value, actor=user).save()

    with pytest.raises(TypeError):
        Setting.get_string('tests', 'setting1')

    assert Setting.get_string(
        'tests', 'setting1', default='the default') == 'the default'


def test_get_list_setting(user):
    from ideascube.models import Setting

    Setting.set('tests', 'setting1', [1, '2'], user)
    assert Setting.objects.count() == 1

    assert Setting.get_list('tests', 'setting1') == [1, '2']


def test_get_unexistent_list_setting():
    from ideascube.models import Setting

    with pytest.raises(Setting.DoesNotExist):
        Setting.get_list('tests', 'setting1')

    assert Setting.get_list(
        'tests', 'setting1', default=['the', 'default']) == ['the', 'default']


@pytest.mark.parametrize(
    'value',
    [
        True, 42, None, 'value',
    ],
    ids=[
        'boolean', 'int', 'none', 'string',
    ])
def test_get_nonlist_setting(value, user):
    from ideascube.models import Setting

    Setting.set('tests', 'setting1', value, user)

    with pytest.raises(TypeError):
        Setting.get_list('tests', 'setting1')

    assert Setting.get_list(
        'tests', 'setting1', default=['the', 'default']) == ['the', 'default']
