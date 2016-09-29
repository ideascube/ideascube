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
    }
]
