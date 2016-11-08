"""KoomBook conf"""
from .kb import *  # noqa

LANGUAGE_CODE = 'en'
IDEASCUBE_NAME = 'P2PU KOOMBOOK'
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
