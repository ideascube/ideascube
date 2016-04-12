# -*- coding: utf-8 -*-
"""Ideaxbox for FAP in Sénégal"""
from .idb import *  # noqa
from django.utils.translation import ugettext_lazy as _

IDEASCUBE_NAME = u"Futur au Présent"
IDEASCUBE_PLACE_NAME = _("city")
COUNTRIES_FIRST = ['SN']
TIME_ZONE = None
LANGUAGE_CODE = 'fr'
LOAN_DURATION = 14
MONITORING_ENTRY_EXPORT_FIELDS = ['serial', 'user_id', 'birth_year', 'gender']
USER_FORM_FIELDS = (
    ('Ideasbox', ['serial', 'box_awareness']),
    (_('Personal informations'), ['short_name', 'full_name', 'birth_year', 'gender', 'id_card_number']),  # noqa
    (_('Family'), ['marital_status', 'family_status', 'children_under_12', 'children_under_18', 'children_above_18']),  # noqa
    (_('In the town'), ['current_occupation', 'school_level']),
    (_('Language skills'), ['en_level']),
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
        'languages': ['fr', 'wo']
    },
    {
        'id': 'gutenberg',
        'lang': 'fr',
    },
    {
        'id': 'cest-pas-sorcier',
    },
    {
        'id': 'wikisource',
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
        'id' : 'dirtybiology',
        'languages': ['fr']
    },
    {
        'id': 'ubuntudoc',
        'languages': ['fr']
    },
    {
        'id': 'wikistage',
        'languages': ['fr']
    },
    {
        'id': 'maps',
        'maps': [
            (_('World'), 'world.map'),
            ('Sénégal', 'senegal.map'),
        ]
    },
]
