import logging


__all__ = [
    'get_config',
    'reset_config',
    'set_config',
]


logger = logging.getLogger(__name__)
IMPOSSIBLE_MESSAGE = (
    'The stored value for %s is of type %s instead of %s. This should never '
    'have happened.')


def get_config(namespace, key):
    """Get a configuration option

    Args:
        namespace (str): The configuration namespace.
        key (str): The configuration key inside the namespace.

    Returns:
        The current value for this option. Its type will be the one defined in
            the registry for this configuration option.

    Raises:
        ideascube.configuration.exceptions.NoSuchConfigurationNamespaceError:
            The requested namespace does not exist.
        ideascube.configuration.exceptions.NoSuchConfigurationKeyError:
            The requested key does not exist in the requested namespace.
    """
    from .models import Configuration
    from .registry import get_default_value, get_expected_type

    default_value = get_default_value(namespace, key)
    expected_type = get_expected_type(namespace, key)

    try:
        config = Configuration.objects.get(namespace=namespace, key=key)

    except Configuration.DoesNotExist:
        return default_value

    if not isinstance(config.value, expected_type):
        logger.error(IMPOSSIBLE_MESSAGE % (
            config, type(config.value), expected_type))
        return default_value

    return config.value


def reset_config(namespace, key):
    """Reset a configuration option to its default value

    Args:
        namespace (str): The configuration namespace.
        key (str): The configuration key inside the namespace.

    Raises:
        ideascube.configuration.exceptions.NoSuchConfigurationNamespaceError:
            The requested namespace does not exist.
        ideascube.configuration.exceptions.NoSuchConfigurationKeyError:
            The requested key does not exist in the requested namespace.
    """
    from .models import Configuration
    from .registry import get_expected_type

    expected_type = get_expected_type(namespace, key)

    try:
        config = Configuration.objects.get(namespace=namespace, key=key)

    except Configuration.DoesNotExist:
        # The configuration had never been modified, nothing to reset
        return

    if not isinstance(config.value, expected_type):
        logger.error(
            IMPOSSIBLE_MESSAGE % (config, type(config.value), expected_type))

    config.delete()


def set_config(namespace, key, value, actor):
    """Set a configuration option

    Args:
        namespace (str): The configuration namespace.
        key (str): The configuration key inside the namespace.
        value: The new value for the option. It should be of the type defined
            in the registry for this configuration option.
        actor (User): The staff user performing the configuration change, for
            audit purposes.

    Raises:
        ideascube.configuration.exceptions.NoSuchConfigurationNamespaceError:
            The requested namespace does not exist.
        ideascube.configuration.exceptions.NoSuchConfigurationKeyError:
            The requested key does not exist in the requested namespace.
        ideascube.configuration.exceptions.InvalidConfigurationValueError:
            The provided value is not the expected type.

    Examples:
        In the context of a view, with a `request` available, one could do:

        >>> set_config('foo', 'bar', 'the value', request.user)
    """
    from .exceptions import InvalidConfigurationValueError
    from .models import Configuration
    from .registry import get_expected_type

    expected_type = get_expected_type(namespace, key)

    if not isinstance(value, expected_type):
        raise InvalidConfigurationValueError(
            namespace, key, expected_type, type(value))

    Configuration.objects.update_or_create(
        namespace=namespace, key=key,
        # Set the actor_id here, not the actor, because when running from a
        # migration the actor object would be an instance of `__fake__.User`
        defaults={'value': value, 'actor_id': actor.id})
