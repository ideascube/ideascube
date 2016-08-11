"""Ideasbox Malakasa, Grece"""
from .idb import *  # noqa
from django.utils.translation import ugettext_lazy as _

COUNTRIES_FIRST = ['AF', 'GR', 'IR', 'PK', 'SY']
TIME_ZONE = 'Europe/Athens'
LANGUAGE_CODE = 'en'
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
        'languages': ['ps', 'ar', 'en', 'el', 'fa']
    },
    {
        'id': 'wikisource',
        'languages': ['ar', 'en', 'el', 'fa']
    },
    {
        'id': 'wikibooks',
        'languages': ['ar', 'en', 'el', 'fa']
    },
    {
        'id': 'wiktionary',
        'languages': ['ps', 'ar', 'en', 'el', 'fa']
    },
    {
        'id': 'wikiversity',
        'languages': ['ps', 'ar', 'en', 'el']
    },
    {
        'id': 'wikiquote',
        'languages': ['ar', 'en', 'el']
    },
    {
        'id': 'vikidia',
        'languages': ['en']
    },
    {
        'id': 'bil-tunisia',
        'languages': ['ar']
    },
    {
        'id': 'mullah-piaz-digest',
        'languages': ['fa']
    },
    {
        'id': 'khanacademy',
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
            ('ted-ed.en', 'Education'),
        ]
    },
    {
        'id': 'w2eu',
    },
    {
        'id': 'maps',
        'maps': [
            ('World', 'world.map'),
            ('Athens', 'athens.map'),
        ]
    }
]
