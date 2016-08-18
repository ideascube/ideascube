import pytest

from ideascube.configuration.exceptions import (
    NoSuchConfigurationKeyError, NoSuchConfigurationNamespaceError,
)
from ideascube.configuration.registry import (
    get_config_data, get_expected_type,
)


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
