"""Configuration for a demo server hosted here, at BSF Headquarters"""
from .idb import *  # noqa

ALLOWED_HOSTS = ['.demo.ideascube.org', '.ideasbox.lan.', 'localhost']
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
        'id': 'gutenberg',
        'lang': 'mul',
    },
    {
        'id': 'wikipedia',
        'languages': ['en','es','ar']
    },
    {
        'id': 'vikidia',
        'languages': ['en']
    },
    {
        'id': 'khanacademy',
    },
    {
        'id': 'ted',
        'sessions': [
            ('tedbusiness.en', 'Business'),
            ('teddesign.en', 'Design'),
            ('tedentertainment.en', 'Entertainment'),
            ('tedglobalissues.en', 'Global Issues'),
            ('tedscience.en', 'Science'),
            ('tedtechnology.en', 'Technology'),
        ]
    },
    {
        'id': 'bil-tunisia',
        'languages': ['ar']
    },
    {
        'id': 'mullah-piaz-digest',
    },
    {
        'id': 'maps',
        'maps': [
            ('World', 'world.map'),
            ('Athens', 'athens.map'),
        ]
    }
]
