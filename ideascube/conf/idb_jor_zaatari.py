"""Ideaxbox for Zaatari, Jordan"""
from .idb import *  # noqa
from django.utils.translation import ugettext_lazy as _

IDEASCUBE_PLACE_NAME = _("city")
COUNTRIES_FIRST = ['SY', 'JO']
TIME_ZONE = 'Asia/Amman'
LANGUAGE_CODE = 'ar'
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
        'id': 'khanacademy',
    },
    {
        'id': 'wikipedia',
        'languages': ['en','ar']
    },
    {
        'id': 'wiktionary',
        'languages': ['en', 'ar']
    },
    {
        'id': 'wikiversity',
        'languages': ['en', 'ar']
    },
    {
        'id': 'wikibooks',
        'languages': ['en', 'ar']
    },
    {
        'id': 'wikisource',
        'languages': ['en', 'ar']
    },
    {
        'id': 'wikiquote',
        'languages': ['en', 'ar']
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
            ('tedmed.en', 'Medical'),
        ]
    },
    {
        'id': 'gutenberg',
        'lang': ['en', 'fr']
    },
    {
        'id': 'crashcourse',
        'languages': ['en']
    },
    {
        'id': 'vikidia',
        'languages': ['en']
    },
]
