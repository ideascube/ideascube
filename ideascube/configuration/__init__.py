__all__ = [
    'set_config',
]


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
