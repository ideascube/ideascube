"""Ideasbox Cultura, France"""
from .idb_fra import *  # pragma: no flakes
from django.utils.translation import ugettext_lazy as _

IDEASCUBE_NAME = u"Cultura"
USER_FORM_FIELDS = (
    (_('Personal informations'), ['serial', 'short_name', 'full_name', 'latin_name', 'birth_year', 'gender']),  # noqa
)
HOME_CARDS = HOME_CARDS + [  # pragma: no flakes
    {
        'id': 'cpassorcier.old',
    },
    {
        'id': 'wikisource.old',
    },
    {
        'id': 'ted.old',
    },
    {
        'id': 'ubuntudoc.old',
    },
]
