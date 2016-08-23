# -*- coding: utf-8 -*-
"""KoomBook conf"""
from .kb import *  # noqa

LANGUAGE_CODE = 'en'
IDEASCUBE_NAME = 'Ambassade De France'
HOME_CARDS = STAFF_HOME_CARDS + [
    {
        'id': 'blog',
    },
    {
        'id': 'mediacenter',
    },
    {
        'id': 'wikipedia',
        'languages': ['fr', 'en', 'sw']
    },
    {
        'id': 'khanacademy',
    },
    {
        'id': 'wiktionary',
        'languages': ['en', 'fr', 'sw']
    },
    {
        'id': 'wikisource',
        'languages': ['fr', 'en']
    },
    {
        'id': 'vikidia',
        'languages': ['en', 'fr']
    },
    {
        'id': 'gutenberg',
        'lang': 'mul',
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
            ('tedxgeneva2014.fr', 'Geneva 2014'),
            ('tedxlausanne2012.fr', 'Lausanne 2012'),
            ('tedxlausanne2013.fr', 'Lausanne 2013'),
            ('tedxlausanne2014.fr', 'Lausanne 2014'),
        ]
    },
    {
        'id': 'wikibooks',
        'languages': ['fr', 'en']
    },
    {
        'id': 'wikiversity',
        'languages': ['en', 'fr']
    },
    {
        'id': 'cest-pas-sorcier',
    },
    {
        'id': 'dirtybiology',
        'languages': ['fr']
    },
    {
        'id': 'les-fondamentaux',
        'languages': ['fr']
    },
    {
        'id': 'universcience',
        'languages': ['fr']
    },
    {
        'id': 'biologie-tout-compris',
        'languages': ['fr']
    },
    {
        'id': 'bouquineux'
    },
    {
        'id': 'deus-ex-silicium',
        'languages': ['fr']
    },
    {
        'id': 'e-penser',
        'languages': ['fr']
    },
]
