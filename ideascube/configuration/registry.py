from __future__ import unicode_literals

from .exceptions import (
    NoSuchConfigurationKeyError,
    NoSuchConfigurationNamespaceError,
)


# Please try and keep this stored in alphabetical order
REGISTRY = {
    # 'namespace': {
    #     'key': {
    #         'type': str,
    #     },
    # },
    'server': {
        'site-name': {
            'type': str,
        },
    },
}


def get_config_data(namespace, key):
    try:
        namespace_registry = REGISTRY[namespace]

    except KeyError:
        raise NoSuchConfigurationNamespaceError(namespace)

    try:
        return namespace_registry[key]

    except KeyError:
        raise NoSuchConfigurationKeyError(namespace, key)


def get_expected_type(namespace, key):
    return get_config_data(namespace, key)['type']
