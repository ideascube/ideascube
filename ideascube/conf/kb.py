from .base import *  # noqa

ALLOWED_HOSTS = ['.koombook.lan', 'localhost', '127.0.0.1']
TIME_ZONE = None
DOMAIN = 'koombook.lan'
BACKUP_FORMAT = 'gztar'
STAFF_HOME_CARDS = [c for c in STAFF_HOME_CARDS  # pragma: no flakes
                    if c['url'] in ['user_list', 'server:power',
                                    'server:wifi']]

HOME_CARDS = STAFF_HOME_CARDS + [
    {
        'id': 'blog',
    },
    {
        'id': 'mediacenter',
    },
    {
        'id': 'khanacademy',
    },
]
