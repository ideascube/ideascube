# -*- coding: utf-8 -*-
"""KoomBook conf"""
from .kb import *  # noqa

LANGUAGE_CODE = 'fr'
IDEASCUBE_NAME = 'UNIVERSITE RDC'
HOME_CARDS = STAFF_HOME_CARDS + [
    {
        'id': 'koombookedu',
    },
    {
        'id': 'wikipedia.old',
    },
]
