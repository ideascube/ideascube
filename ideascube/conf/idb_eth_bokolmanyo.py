"""Bokolmanyo box in Ethiopia"""
from .idb import *  # noqa
from django.utils.translation import ugettext_lazy as _

IDEASCUBE_NAME = u"Bokolmanyo"
COUNTRIES_FIRST = ['SO', 'ET']
TIME_ZONE = 'Africa/Addis_Ababa'
LANGUAGE_CODE = 'en'
MONITORING_ENTRY_EXPORT_FIELDS = ['serial', 'refugee_id', 'birth_year',
                                  'gender']
USER_FORM_FIELDS = (
    ('Ideasbox', ['serial', 'box_awareness']),
    (_('Personal informations'), ['refugee_id', 'short_name', 'full_name', 'latin_name', 'birth_year', 'gender']),  # noqa
    (_('Family'), ['marital_status', 'family_status', 'children_under_12', 'children_under_18', 'children_above_18']),  # noqa
    (_('In the camp'), ['camp_entry_date', 'camp_activities', 'current_occupation', 'camp_address']),  # noqa
    (_('Origin'), ['country', 'city', 'country_of_origin_occupation', 'school_level', 'is_sent_to_school']),  # noqa
    (_('Language skills'), ['ar_level', 'en_level']),
    (_('National residents'), ['id_card_number']),
)

HOME_CARDS = STAFF_HOME_CARDS + [
    {
        'id': 'blog',
    },
    {
        'id': 'mediacenter',
    },
    {
        'id': 'library',
    },
    {
        'id': 'wikipedia.old',
    },
    {
        'id': 'khanacademy',
    },
    {
        'id': 'vikidia.old',
    },
    {
        'id': 'gutenberg.old',
    },
]
