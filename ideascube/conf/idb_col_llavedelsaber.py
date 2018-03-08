"""Configuration for Llave Del Saber, Colombia"""
from .idb import *  # pragma: no flakes
from django.utils.translation import ugettext_lazy as _

LANGUAGE_CODE = 'es'

USER_FORM_FIELDS = USER_FORM_FIELDS + (  # pragma: no flakes
        (_('Personal informations'), ['disabilities']),
)

USER_IMPORT_FORMATS = (
    ('llavedelsaber', 'Llave del Saber'),
    ('ideascube', 'Ideascube'),
)
