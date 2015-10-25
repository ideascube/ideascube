import importlib
import os
import re
import socket
import sys

# The normal scenario is that we use the hostname, but let's make it
# overridable, this is useful for dev and debugging.
IDEASTUBE_HOSTNAME = socket.gethostname()  # Store it for later use.
IDEASTUBE_ID = os.environ.get('IDEASTUBE_ID', IDEASTUBE_HOSTNAME)
IDEASTUBE_ID = re.sub('[^\w_]', '', IDEASTUBE_ID)
sys.stdout.write('IDEASTUBE_ID={}\n'.format(IDEASTUBE_ID))

# Every box will have some edge specific needs, such as a specific user model,
# we manage this with per box settings, but we want those specific settings
# to be versionned, for two reasons: easier to debug when there is no hidden
# local config, and easier to manage code upgrade.
try:
    sub = importlib.import_module(".conf." + IDEASTUBE_ID, package="ideastube")
except ImportError:
    from .conf import dev as sub
except Exception as e:
    print(e)
finally:
    # Make it available as a settings, to be able to display it in the admin.
    SETTINGS_MODULE = sub.__name__
    sys.stdout.write('Importing settings from %s\n' % SETTINGS_MODULE)
    ldict = locals()
    for k in sub.__dict__:
        if k.isupper() and not k.startswith('__') or not k.endswith('__'):
            ldict[k] = sub.__dict__[k]
    USER_DATA_FIELDS = []
    for section, fields in USER_FORM_FIELDS:  # noqa
        USER_DATA_FIELDS.extend(fields)
