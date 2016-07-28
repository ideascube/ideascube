# -*- coding: utf-8 -*-
"""KoomBook conf"""
from .kb import *  # noqa

LANGUAGE_CODE = 'es'
HOME_CARDS = STAFF_HOME_CARDS + [
    {
        'id': 'blog',
    },
    {
        'id': 'mediacenter',
    },
    {
        'id': 'gutenberg',
        'lang': 'es',
    },
    {
        'id': 'wikipedia',
        'languages': ['es']
    },
    {
        'id': 'khanacademy',
    },
]
