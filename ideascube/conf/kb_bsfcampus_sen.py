# -*- coding: utf-8 -*-

"""KoomBook conf"""

from .base import *  # noqa
from django.utils.translation import ugettext_lazy as _

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('DEBUG', True))

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['.koombook.lan.', 'localhost', '127.0.0.1']

LANGUAGE_CODE = 'fr'

TIME_ZONE = None

# Ideas Box specifics
STORAGE_ROOT = '/media/hdd/ideascube/storage' 

IDEASCUBE_NAME = 'BSF Campus SÉNÉGAL'

DOMAIN = 'koombook.lan'

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
        'id': 'wikipedia',
    },
    {
        'id': 'khanacademy',
    },
    # {
    #     'category': 'learn',
    #     'url': 'http://mydomain.fr',
    #     'title': 'The title of my custom card',
    #     'description': 'The description of my custom card',
    #     'img': '/img/wikipedia.png',
    #     'fa': 'fax',
    # },
]

IDEASCUBE_BODY_ID = 'koombook'
