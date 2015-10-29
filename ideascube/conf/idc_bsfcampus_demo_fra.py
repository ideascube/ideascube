# -*- coding: utf-8 -*-

"""KoomBook conf"""

from .base import *  # noqa
from django.utils.translation import ugettext_lazy as _

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('DEBUG', True))

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['.ideasbox.lan.', 'localhost', '127.0.0.1']

LANGUAGE_CODE = 'fr'

TIME_ZONE = None

# Ideas Box specifics

IDEASCUBE_NAME = 'BSF Campus CAMEROUN'

DOMAIN = 'ideasbox.lan'

BACKUP_FORMAT = 'gztar'

STAFF_HOME_CARDS = [c for c in STAFF_HOME_CARDS if c['url'] in ['user_list', 'server:power', 'server:backup']]

HOME_CARDS = STAFF_HOME_CARDS + [
    {
        'id': 'blog',
    },
    {
        'id': 'mediacenter',
    },
    {
        'id': 'bsfcampus',
    },
    {
        'id': 'wikipedia',
    },
    {
        'id': 'khanacademy',
    },
    {
        'id': 'wikisource',
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
    {
        'id': 'software',
    },
    {
        'id': 'ubuntudoc',
    },
]

IDEASCUBE_BODY_ID = 'Ideasbox'
