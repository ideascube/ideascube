"""KoomBook conf"""
from .kb import *  # noqa

LANGUAGE_CODE = 'fr'
IDEASCUBE_NAME = 'Institut Français Burundi'
HOME_CARDS = STAFF_HOME_CARDS + [
    {
        'id': 'blog',
    },
    {
        'id': 'mediacenter',
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
        'id': 'appinventor',
    },
    {
        'id': 'gutenberg.old',
    },
]
