# -*- coding: utf-8 -*-
"""KoomBook conf"""
from .kb import *  # noqa
from django.utils.translation import ugettext_lazy as _

LANGUAGE_CODE = 'fr'
IDEASCUBE_NAME = 'BabyLab'
HOME_CARDS = STAFF_HOME_CARDS + [
    {
        'id': 'blog',
    },
    {
        'id': 'mediacenter',
    },
    {
        'id': 'bsfcampus',
    },
    {
        'id': 'khanacademy',
    },
    {
        'id': 'wikistage',
        'languages': ['fr']
    },
    {
        'id': 'wikimooc',
    },
    {
        'id': 'vikidia',
        'languages': ['fr']
    },
    {
        'id': 'universcience',
        'languages': ['fr']
    },
    {
        'id': 'e-penser',
        'languages': ['fr']
    },
    {
        'id': 'deus-ex-silicium',
        'languages': ['fr']
    },
    {
        'id': 'cest-pas-sorcier',
    },
    {
        'id': 'wikipedia',
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
]
