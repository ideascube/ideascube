# -*- coding: utf-8 -*-
"""Mapoon box in Australia"""
from .base import *  # noqa
from django.utils.translation import ugettext_lazy as _

IDEASBOX_NAME = u"Mapoon"
COUNTRIES_FIRST = ['AU']
TIME_ZONE = 'Australia/Darwin'
LANGUAGE_CODE = 'en'
MONITORING_ENTRY_EXPORT_FIELDS = ['serial', 'user_id', 'birth_year', 'gender']
USER_FORM_FIELDS = (
    ('Ideasbox', ['serial', 'box_awareness']),
    (_('Personal informations'), ['short_name', 'full_name', 'latin_name', 'birth_year', 'gender', 'id_card_number']),  # noqa
    (_('Family'), ['marital_status', 'family_status', 'children_under_12', 'children_under_18', 'children_above_18']),  # noqa
    (_('In the town'), ['current_occupation', 'school_level', 'is_sent_to_school']),  # noqa
    (_('Language skills'), ['en_level']),
)
