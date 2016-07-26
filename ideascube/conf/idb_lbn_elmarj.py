# -*- coding: utf-8 -*-
"""El Marj box in Lebanon"""
from .idb import *  # noqa
IDEASCUBE_NAME = u"El Marj Lebanon"  # Fixme
COUNTRIES_FIRST = ['LB', 'SY', 'JO', 'PS']
TIME_ZONE = 'Asia/Beirut'
LANGUAGE_CODE = 'ar'

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
    },
    {
        'id': 'wikipedia',
        'languages': ['ar']
    },
    {
        'id': 'wiktionary',
        'languages': ['ar']
    },
    {
        'id': 'wikiversity',
        'languages': ['ar']
    },
    {
        'id': 'wikibooks',
        'languages': ['ar']
    },
    {
        'id': 'wikisource',
        'languages': ['ar']
    },
    {
        'id': 'wikiquote',
        'languages': ['ar']
    },
    {
        'id': 'bil-tunisia',
        'languages': ['ar']
    },
    {
        'id': 'maps',
        'maps': [
            ('World', 'world.map'),
            ('Lebanon', 'lebanon.map'),
        ]
    },
]
