import importlib
import os
import re
import socket
import sys

from django.utils.termcolors import colorize


def log(s):
    sys.stdout.write(colorize(s, fg='cyan') + '\n')


# The normal scenario is that we use the hostname, but let's make it
# overridable, this is useful for dev and debugging.
IDEASCUBE_HOSTNAME = socket.gethostname()  # Store it for later use.
IDEASCUBE_ID = os.environ.get('IDEASCUBE_ID', IDEASCUBE_HOSTNAME)
IDEASCUBE_ID = re.sub('[^\w_]', '', IDEASCUBE_ID)
log('IDEASCUBE_ID={}'.format(IDEASCUBE_ID))

# Every box will have some edge specific needs, such as a specific user model,
# we manage this with per box settings, but we want those specific settings
# to be versionned, for two reasons: easier to debug when there is no hidden
# local config, and easier to manage code upgrade.
_SETTINGS_PACKAGE = os.environ.get('IDEASCUBE_SETTINGS_PACKAGE', 'ideascube')
_SETTINGS_MODULE = '.conf.' + IDEASCUBE_ID

try:
    sub = importlib.import_module(_SETTINGS_MODULE, package=_SETTINGS_PACKAGE)

except (ImportError, SystemError):
    # No specific config for this box
    log('Could not import settings from %s%s'
        % (_SETTINGS_PACKAGE, _SETTINGS_MODULE))

    from .conf import base as sub

log('Importing settings from %s' % sub.__name__)
ldict = locals()
for k in sub.__dict__:
    if k.isupper() and not k.startswith('__') or not k.endswith('__'):
        ldict[k] = sub.__dict__[k]
USER_DATA_FIELDS = []
for section, fields in USER_FORM_FIELDS:  # pragma: no flakes
    USER_DATA_FIELDS.extend(fields)

# Allow server settings to only define STORAGE_ROOT without needing to
# redefine all ROOTS like settings.
BACKUPED_ROOT = ldict.get('BACKUPED_ROOT') or os.path.join(STORAGE_ROOT, 'main')  # pragma: no flakes
MEDIA_ROOT = ldict.get('MEDIA_ROOT') or os.path.join(BACKUPED_ROOT, 'media')  # noqa
STATIC_ROOT = ldict.get('STATIC_ROOT') or os.path.join(STORAGE_ROOT, 'static')  # pragma: no flakes
CATALOG_CACHE_ROOT = (
    ldict.get('CATALOG_CACHE_ROOT') or '/var/cache/ideascube/catalog')
CATALOG_STORAGE_ROOT = (
    ldict.get('CATALOG_STORAGE_ROOT')
    or os.path.join(BACKUPED_ROOT, 'catalog'))

if not getattr(ldict, 'DATABASES', None):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BACKUPED_ROOT, 'default.sqlite'),
        },
        'transient': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(STORAGE_ROOT, 'transient.sqlite'),  # pragma: no flakes
        }
    }

FILE_UPLOAD_PERMISSIONS = 0o644
