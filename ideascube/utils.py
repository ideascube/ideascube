import sys

from django.conf import settings


class classproperty(property):
    """
    Use it to decorate a classmethod to make it a "class property".
    """
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


def get_server_name():
    # Import here to avoid cyclic import
    from ideascube.models import Setting

    # This used to be a setting. Keep honoring it for now, so we don't break
    # expectations from users of already deployed boxes.
    default = getattr(settings, 'IDEASCUBE_NAME', 'Ideas Cube')

    return Setting.get_string('server', 'site-name', default=default)


# We do not use functool.partial cause we want to mock stderr for unittest
# If we use partial we keep a ref to the original sys.stderr and output is not
# captured.
def printerr(*args, **kwargs):
    kwargs['file'] = sys.stderr
    kwargs['flush'] = True
    return print(*args, **kwargs)
