# -*- coding: utf-8 -*-
"""KoomBook conf"""
from .kb import *  # noqa
from django.utils.translation import ugettext_lazy as _

LANGUAGE_CODE = 'fr'
IDEASCUBE_NAME = 'Conakry'
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
        'id': 'koombookedu',
    },
    {
        'id': 'wikipedia',
        'languages': ['fr'],
    },
    {
        'id': 'cest-pas-sorcier',
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
        'id': 'universcience',
        'languages': ['fr']
    },
]
