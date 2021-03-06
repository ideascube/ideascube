from .base import *  # pragma: no flakes

from tzlocal import get_localzone


TIME_ZONE = get_localzone().zone
BACKUP_FORMAT = 'gztar'
STAFF_HOME_CARDS = [c for c in STAFF_HOME_CARDS  # pragma: no flakes
                    if c['url'] in ['user_list', 'server:settings']]

BUILTIN_APP_CARDS = ['blog', 'mediacenter']
EXTRA_APP_CARDS = ['kolibri']
