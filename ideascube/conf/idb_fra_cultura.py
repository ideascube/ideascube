"""Ideasbox Cultura, France"""
from .idb_fra import *  # pragma: no flakes
from django.utils.translation import ugettext_lazy as _

IDEASCUBE_NAME = "Cultura"
USER_FORM_FIELDS = (
    (_('Personal informations'), ['serial', 'short_name', 'full_name', 'latin_name', 'birth_year', 'gender']),  # noqa
)
