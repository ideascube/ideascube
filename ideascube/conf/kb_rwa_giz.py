"""KoomBook conf"""
from .kb import *  # pragma: no flakes

LANGUAGE_CODE = 'en'
IDEASCUBE_NAME = 'GIZ'
HOME_CARDS = STAFF_HOME_CARDS + [  # pragma: no flakes
    {
        'id': 'blog',
    },
    {
        'id': 'mediacenter',
    },
]
