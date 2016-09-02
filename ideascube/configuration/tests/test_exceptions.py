from ideascube.configuration.exceptions import (
    InvalidConfigurationValueError,
    NoSuchConfigurationKeyError,
    NoSuchConfigurationNamespaceError,
)


def test_invalid_configuration_value():
    e = InvalidConfigurationValueError('namespace', 'key', int, str)
    assert str(e) == (
        'Invalid type for configuration key "namespace.key": expected '
        '<class \'int\'>, got <class \'str\'>')


def test_no_such_configuration_key():
    e = NoSuchConfigurationKeyError('namespace', 'key')
    assert str(e) == 'Unknown configuration key: "namespace.key"'


def test_no_such_configuration_namespace():
    e = NoSuchConfigurationNamespaceError('namespace')
    assert str(e) == 'Unknown configuration namespace: "namespace"'
