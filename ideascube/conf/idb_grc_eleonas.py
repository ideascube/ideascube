# -*- coding: utf-8 -*-
"""Library Without Borders box in Athenes, Grece"""
from .idb import *  # noqa
from django.utils.translation import ugettext_lazy as _

IDEASCUBE_NAME = u"Eleonas"
IDEASCUBE_PLACE_NAME = _("camp")
COUNTRIES_FIRST = ['AF', 'GR', 'IR', 'PK', 'SY']
TIME_ZONE = 'Europe/Athens'
LANGUAGE_CODE = 'en'
LOAN_DURATION = 14
USER_FORM_FIELDS = (
    (_('Personal informations'), ['serial', 'short_name', 'full_name', 'latin_name', 'birth_year', 'gender']),  # noqa
    (_('In the town'), ['current_occupation', 'school_level', 'phone', 'email']),  # noqa
    (_('Language skills'), ['en_level', 'ar_level', 'fa_level']),
)

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
        'id': 'wikipedia',
        'languages': ['ps', 'ar', 'en', 'ur', 'fa']
    },
    {
        'id': 'khanacademy',
    },
    {
        'id': 'gutenberg',
        'lang': 'mul',
    },
    {
        'id': 'w2eu',
    },
    {
        'id': 'maps',
        'maps': [
            ('World', 'world.map'),
            ('Athens', 'athens.map'),
            ('Lesvos', 'lesvos.map'),
        ]
    }
]
