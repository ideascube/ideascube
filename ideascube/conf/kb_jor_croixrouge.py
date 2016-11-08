"""KoomBook conf"""
from .kb import *  # noqa

LANGUAGE_CODE = 'ar'
IDEASCUBE_NAME = 'Red Cross'
HOME_CARDS = STAFF_HOME_CARDS + [
    {
        'id': 'blog',
    },
    {
        'id': 'mediacenter',
    },
    {
        'id': 'khanacademy',
    }
]
