"""Bardarash in Kurdistan, Iraq"""
from .azraq import *  # noqa
from django.utils.translation import ugettext_lazy as _


USER_FORM_FIELDS = (
    ('Ideasbox', ['serial', 'box_awareness']),
    (_('Personal informations'), ['short_name', 'full_name', 'latin_name', 'birth_year', 'gender', 'country_of_origin_occupation', 'school_level']),  # noqa
    (_('Family'), ['marital_status', 'family_status', 'children_under_12', 'children_under_18', 'children_above_18']),  # noqa
    (_('In the camp'), ['camp_entry_date', 'camp_activities', 'current_occupation', 'camp_address']),  # noqa
    (_('Language skills'), ['ar_level', 'ku_level', 'sdb_level', 'en_level']),
)
MONITORING_ENTRY_EXPORT_FIELDS = ['serial', 'birth_year', 'gender']


ENTRY_ACTIVITY_CHOICES = []

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
        'id': 'wiktionary',
        'languages': ['en', 'ar']
    },
    {
        'id': 'wikiversity',
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
        ]
    },
    {
        'id': 'gutenberg',
        'lang': 'en',
    },
    {
        'id': 'bil-tunisia',
        'languages': ['ar']
    },
]
