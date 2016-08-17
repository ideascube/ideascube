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
        'id': 'library',
    },
    {
        'id': 'mediacenter',
    },
    {
        'id': 'wikipedia',
        'languages': ['fr','rn','sw']
    },
    {
        'id': 'vikidia',
        'languages': ['fr']
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
            ('tedxgeneva2014.fr', 'Geneva 2014'),
            ('tedxlausanne2012.fr', 'Lausanne 2012'),
            ('tedxlausanne2013.fr', 'Lausanne 2013'),
            ('tedxlausanne2014.fr', 'Lausanne 2014'),
            ('tedxlausannechange2013.fr', 'Lausanne Exchange 2013'),
        ]
    },
    {
        'id': 'maps',
        'maps': [
            ('World', 'world.map'),
            ('Burundi', 'burundi.map'),
        ]
    }
]
