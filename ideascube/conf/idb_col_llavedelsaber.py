"""Configuration for Llave Del Saber, Colombia"""
from .idb import *  # noqa

LANGUAGE_CODE = 'es'
DOMAIN = 'bibliotecamovil.lan'
ALLOWED_HOSTS = ['.bibliotecamovil.lan', 'localhost']

USER_FORM_FIELDS = USER_FORM_FIELDS + (
        (_('Personal informations'), ['extra']),
)

USER_EXTRA_FIELD_LABEL = 'Etnicidad'
