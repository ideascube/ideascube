from .base import *  # pragma: no flakes


ALLOWED_HOSTS = ['.ideasbox.lan', 'localhost']
DOMAIN = 'ideasbox.lan'

HOME_CARDS = STAFF_HOME_CARDS + [  # pragma: no flakes
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
