from .base import *  # noqa

ALLOWED_HOSTS = ['.ideasbox.lan', 'localhost']
DOMAIN = 'ideasbox.lan'

STAFF_HOME_CARDS = [c for c in STAFF_HOME_CARDS
                    if c['url'] not in ['server:battery']]

HOME_CARDS = STAFF_HOME_CARDS + [
    {
        'id': 'blog',
    },
    {
        'id': 'mediacenter',
    },
    {
        'id': 'library',
    },
    {
        'id': 'khanacademy',
    }
]
