"""Configuration for a demo server hosted here, at BSF Headquarters"""
from .idb import *  # noqa

ALLOWED_HOSTS = ['.demo.ideascube.org', '.ideasbox.lan', 'localhost']
DOMAIN = 'demo.ideascube.org'

LANGUAGE_CODE = 'es'
HOME_CARDS = STAFF_HOME_CARDS + [
    {
        'id': 'blog',
    },
    {
        'id': 'library',
    },
    {
        'id': 'mediacenter',
    },
    {
        'id': 'khanacademy',
    }
]
