from .base import *  # noqa

STAFF_HOME_CARDS = [c for c in STAFF_HOME_CARDS
                    if c['url'] not in ['server:power', 'server:wifi']]

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
        'id': 'wikipedia',
    },
    {
        'id': 'khanacademy',
    },
    {
        'id': 'vikidia',
    },
    {
        'id': 'gutenberg',
    },
]
