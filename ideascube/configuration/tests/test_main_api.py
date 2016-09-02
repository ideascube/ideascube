from datetime import datetime, timezone

import freezegun

import pytest

from ideascube.configuration import get_config, set_config
from ideascube.configuration.exceptions import (
    InvalidConfigurationValueError,
    NoSuchConfigurationKeyError,
    NoSuchConfigurationNamespaceError,
)
from ideascube.configuration.models import Configuration


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'value',
    [
        True, 42, 'A string', ['A', 'list'],
    ],
    ids=[
        'boolean', 'int', 'string', 'list',
    ])
def test_get_configuration(monkeypatch, value, user):
    monkeypatch.setattr(
        'ideascube.configuration.registry.REGISTRY',
        {'tests': {'setting1': {'type': type(value), 'default': "whatever"}}})

    Configuration(
        namespace='tests', key='setting1', value=value, actor=user).save()

    assert get_config('tests', 'setting1') == value


def test_get_configuration_invalid_namespace(monkeypatch):
    monkeypatch.setattr('ideascube.configuration.registry.REGISTRY', {})

    with pytest.raises(NoSuchConfigurationNamespaceError):
        get_config('tests', 'setting1')


def test_get_configuration_invalid_key(monkeypatch):
    monkeypatch.setattr(
        'ideascube.configuration.registry.REGISTRY', {'tests': {}})

    with pytest.raises(NoSuchConfigurationKeyError):
        get_config('tests', 'setting1')


def test_get_configuration_invalid_type(capsys, monkeypatch, user):
    monkeypatch.setattr(
        'ideascube.configuration.registry.REGISTRY',
        {'tests': {'setting1': {'type': int, 'default': 42}}})

    # Store a bad value in the database
    Configuration(
        namespace='tests', key='setting1', value='foo', actor=user).save()

    assert get_config('tests', 'setting1') == 42

    out, err = capsys.readouterr()
    assert out.strip() == ''
    assert err.strip().split(':') == [
        'ERROR', 'ideascube.configuration',
        "The stored value for tests.setting1='foo' is of type <class 'str'> "
        "instead of <class 'int'>. This should never have happened."]


def test_get_default_configuration(monkeypatch):
    monkeypatch.setattr(
        'ideascube.configuration.registry.REGISTRY',
        {'tests': {'setting1': {'type': int, 'default': 42}}})

    assert get_config('tests', 'setting1') == 42


@pytest.mark.parametrize(
    'value1, value2',
    [
        (True, False),
        (42, 43),
        ('A string', 'Another string'),
        (['A', 'list'], ['Another', 'list']),
    ],
    ids=[
        'boolean', 'int', 'string', 'list',
    ])
def test_set_configuration(monkeypatch, value1, value2, user):
    monkeypatch.setattr(
        'ideascube.configuration.registry.REGISTRY',
        {'tests': {'setting1': {'type': type(value1)}}})

    fakenow = datetime.now(tz=timezone.utc)

    with freezegun.freeze_time(fakenow):
        set_config('tests', 'setting1', value1, user)

    assert Configuration.objects.count() == 1

    configuration = Configuration.objects.first()
    assert configuration.namespace == 'tests'
    assert configuration.key == 'setting1'
    assert configuration.value == value1
    assert configuration.actor == user
    assert configuration.date == fakenow
    assert str(configuration) == 'tests.setting1=%r' % value1

    set_config('tests', 'setting1', value2, user)

    assert Configuration.objects.count() == 1

    configuration = Configuration.objects.first()
    assert configuration.namespace == 'tests'
    assert configuration.key == 'setting1'
    assert configuration.value == value2
    assert str(configuration) == 'tests.setting1=%r' % value2


def test_set_configuration_invalid_namespace(monkeypatch, user):
    monkeypatch.setattr('ideascube.configuration.registry.REGISTRY', {})

    with pytest.raises(NoSuchConfigurationNamespaceError):
        set_config('tests', 'setting1', 'value1', user)


def test_set_configuration_invalid_key(monkeypatch, user):
    monkeypatch.setattr(
        'ideascube.configuration.registry.REGISTRY', {'tests': {}})

    with pytest.raises(NoSuchConfigurationKeyError):
        set_config('tests', 'setting1', 'value1', user)


def test_set_configuration_invalid_type(monkeypatch, user):
    monkeypatch.setattr(
        'ideascube.configuration.registry.REGISTRY',
        {'tests': {'setting1': {'type': int}}})

    with pytest.raises(InvalidConfigurationValueError):
        set_config('tests', 'setting1', 'value1', user)
