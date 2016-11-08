"""KoomBook conf"""
from .kb import *  # noqa

LANGUAGE_CODE = 'es'
IDEASCUBE_NAME = 'Nicarali'
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
