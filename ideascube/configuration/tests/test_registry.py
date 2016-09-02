import pytest

from ideascube.configuration.exceptions import (
    NoSuchConfigurationKeyError, NoSuchConfigurationNamespaceError,
)
from ideascube.configuration.registry import (
    get_config_data, get_default_value, get_expected_type,
)


def test_nobody_messed_the_registry():
    from ideascube.configuration.registry import REGISTRY

    for namespaced_keys in REGISTRY.values():
        for config_data in namespaced_keys.values():
            assert 'default' in config_data
            assert 'type' in config_data


def test_get_config_data(monkeypatch):
    monkeypatch.setattr(
        'ideascube.configuration.registry.REGISTRY',
        {
            'namespace1': {
                'key2': {},
                'key1': {'summary': 'The first key'},
            },
            'namespace2': {},
        })

    data = get_config_data('namespace1', 'key1')
    assert data == {'summary': 'The first key'}

    data = get_config_data('namespace1', 'key2')
    assert data == {}

    with pytest.raises(NoSuchConfigurationNamespaceError):
        get_config_data('namespace3', 'any-key')

    with pytest.raises(NoSuchConfigurationKeyError):
        get_config_data('namespace2', 'any-key')


def test_get_default_value(monkeypatch):
    monkeypatch.setattr(
        'ideascube.configuration.registry.REGISTRY',
        {
            'namespace1': {
                'key2': {'default': '42'},
                'key1': {'default': 42},
                'key3': {},
            },
        })

    assert get_default_value('namespace1', 'key1') == 42
    assert get_default_value('namespace1', 'key2') == '42'

    with pytest.raises(KeyError):
        # The 'default' key is mandatory
        assert get_default_value('namespace1', 'key3')


def test_get_expected_type(monkeypatch):
    monkeypatch.setattr(
        'ideascube.configuration.registry.REGISTRY',
        {
            'namespace1': {
                'key2': {'type': str},
                'key1': {'type': int},
                'key3': {},
            },
        })

    assert get_expected_type('namespace1', 'key1') is int
    assert get_expected_type('namespace1', 'key2') is str

    with pytest.raises(KeyError):
        # The 'type' key is mandatory
        assert get_expected_type('namespace1', 'key3')
