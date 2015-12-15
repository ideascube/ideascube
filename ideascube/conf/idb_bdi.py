"""Generic config for Ideasbox of Burundi"""
from .idb import *  # noqa
from django.utils.translation import ugettext_lazy as _

USER_FORM_FIELDS = (
    ('Ideasbox', ['serial', 'box_awareness']),
    (_('Personal informations'), ['refugee_id', 'short_name', 'full_name', 'birth_year', 'gender', 'phone']),  # noqa
    (_('Family'), ['marital_status', 'family_status', 'children_under_12', 'children_under_18', 'children_above_18']),  # noqa
    (_('In the camp'), ['camp_entry_date', 'camp_activities', 'current_occupation', 'camp_address']),  # noqa
    (_('Origin'), ['country', 'city', 'country_of_origin_occupation', 'school_level', 'is_sent_to_school']),  # noqa
    (_('Language skills'), ['rn_level', 'sw_level', 'fr_level']),
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
        'id': 'wikipedia',
    },
    {
        'id': 'khanacademy',
    },
    {
        'id': 'vikidia',
    },
    {
        'id': 'gutenberg',
    },
    {
        'id': 'cpassorcier',
    },
    {
        'id': 'ted',
    },
]
