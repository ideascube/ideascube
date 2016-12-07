"""Configuration for Llave Del Saber, Colombia"""
from .idb import *  # noqa
from django.utils.translation import ugettext_lazy as _

LANGUAGE_CODE = 'es'
DOMAIN = 'bibliotecamovil.lan'
ALLOWED_HOSTS = ['.bibliotecamovil.lan', 'localhost']

USER_FORM_FIELDS = USER_FORM_FIELDS + (
        (_('Personal informations'), ['extra'], ['disabilities']),
)

USER_EXTRA_FIELD_LABEL = 'Etnicidad'
