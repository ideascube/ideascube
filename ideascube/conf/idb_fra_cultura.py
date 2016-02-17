# -*- coding: utf-8 -*-
"""Ideaxbox Cultura, France"""
from .idb import *  # noqa
from django.utils.translation import ugettext_lazy as _

IDEASCUBE_NAME = u"Cultura"
IDEASCUBE_PLACE_NAME = _("city")
COUNTRIES_FIRST = ['FR']
TIME_ZONE = None
LANGUAGE_CODE = 'fr'
LOAN_DURATION = 14
MONITORING_ENTRY_EXPORT_FIELDS = ['serial', 'user_id', 'birth_year', 'gender']
USER_FORM_FIELDS = (
    (_('Personal informations'), ['serial', 'short_name', 'full_name', 'latin_name', 'birth_year', 'gender']),  # noqa
)
HOME_CARDS = HOME_CARDS + [
    {
        'id': 'cpassorcier',
    },
    {
        'id': 'wikisource',
    },
    {
        'id': 'software',
    },
    {
        'id': 'ted',
    },
    {
        'id': 'ubuntudoc',
    },
]
