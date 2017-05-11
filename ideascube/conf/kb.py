from .base import *  # pragma: no flakes

from tzlocal import get_localzone


ALLOWED_HOSTS = ['.koombook.lan', 'localhost', '127.0.0.1']
TIME_ZONE = get_localzone().zone
DOMAIN = 'koombook.lan'
BACKUP_FORMAT = 'gztar'

STAFF_HOME_CARDS = ['user', 'settings']
BUILTIN_APP_CARDS = ['blog', 'mediacenter']
EXTRA_APP_CARDS = ['khanacademy']
