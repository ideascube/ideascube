# -*- coding: utf-8 -*-
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
        'id': 'wikipedia',
        'languages': ['ar', 'en']
    },
    {
        'id': 'khanacademy',
    },
    {
        'id': 'wiktionary',
        'languages': ['en', 'ar']
    },
    {
        'id': 'wikisource',
        'languages': ['ar', 'en']
    },
    {
        'id': 'vikidia',
        'languages': ['en']
    },
    {
        'id': 'gutenberg',
        'lang': 'en',
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
        'id': 'wikiquote',
        'languages': ['ar', 'en']
    },
    {
        'id': 'wikibooks',
        'languages': ['ar', 'en']
    },
    {
        'id': 'wikiversity',
        'languages': ['en', 'ar']
    },
    {
        'id': 'bil-tunisia',
        'languages': ['ar']
    },
]
