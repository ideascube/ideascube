# -*- coding: utf-8 -*-
"""Bardarash in Kurdistan"""
from .azraq import *  # noqa
from django.utils.translation import ugettext_lazy as _

IDEASCUBE_NAME = u"Bardarash"

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
        'languages': ['en', 'ar']
    },
    {
        'id': 'gutenberg',
        'lang': 'mul',
    },
]
