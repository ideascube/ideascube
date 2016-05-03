from .base import *  # noqa

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
        'id': 'wikipedia.old',
    },
    {
        'id': 'khanacademy',
    },
    {
        'id': 'vikidia.old',
    },
    {
        'id': 'gutenberg.old',
    },
]
