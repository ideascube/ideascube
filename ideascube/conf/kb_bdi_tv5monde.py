# -*- coding: utf-8 -*-
"""KoomBook conf"""
from .kb import *  # noqa
from django.utils.translation import ugettext_lazy as _

LANGUAGE_CODE = 'fr'
IDEASCUBE_NAME = 'TV5 Monde Burundi'
HOME_CARDS = STAFF_HOME_CARDS + [
    {
        'id': 'blog',
    },
    {
        'id': 'mediacenter',
    },
    {
        'id': 'wikipedia',
        'languages': ['fr', 'rn', 'en']
    },
    {
        'id': 'gutenberg',
        'lang': 'fr',
    },
    {
        'id': 'khanacademy',
    },
    {
        'id': 'cest-pas-sorcier',
    },
    {
        'id': 'wikisource',
        'languages': ['fr']
    },
    {
        'id': 'wikibooks',
        'languages': ['fr']
    },
    {
        'id': 'wikivoyage',
        'languages': ['fr']
    },
    {
        'id': 'wiktionary',
        'languages': ['fr']
    },
    {
        'id': 'wikiversity',
        'languages': ['fr']
    },
    {
        'id': 'ted',
        'sessions': [
            ('tedxgeneva2014.fr', 'Geneva 2014'),
            ('tedxlausanne2012.fr', 'Lausanne 2012'),
            ('tedxlausanne2013.fr', 'Lausanne 2013'),
            ('tedxlausanne2014.fr', 'Lausanne 2014'),
        ]
    },
    {
        'id': 'ubuntudoc',
        'languages': ['fr']
    },
    {
        'id': 'universcience',
        'languages': ['fr']
    },
]
