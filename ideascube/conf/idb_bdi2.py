"""Generic config for Ideasbox of Burundi, second version"""
from .idb import *  # noqa

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
        'id': 'wikipedia',
        'languages': ['fr','rn','sw']
    },
    {
        'id': 'vikidia',
        'languages': ['fr']
    },
    {
        'id': 'khanacademy',
    },
    {
        'id': 'gutenberg',
        'lang': 'mul',
    },
    {
        'id': 'ted',
        'sessions': [
            ('tedxgeneva2014.fr', 'Geneva 2014'),
            ('tedxlausanne2012.fr', 'Lausanne 2012'),
            ('tedxlausanne2013.fr', 'Lausanne 2013'),
            ('tedxlausanne2014.fr', 'Lausanne 2014'),
            ('tedxlausannechange2013.fr', 'Lausanne Exchange 2013'),
        ]
    },
    {
        'id': 'maps',
        'maps': [
            ('World', 'world.map'),
            ('Burundi', 'burundi.map'),
        ]
    }
]
