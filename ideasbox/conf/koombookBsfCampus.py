# -*- coding: utf-8 -*-

"""KoomBook conf"""

from .base import *  # noqa
from django.utils.translation import ugettext_lazy as _

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('DEBUG', True))

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['.koombook.lan.', 'localhost', '127.0.0.1']

LANGUAGE_CODE = 'fr'

TIME_ZONE = 'Europe/Paris'

# Ideas Box specifics
STORAGE_ROOT = '/media/hdd/ideasServer/storage' 

IDEASBOX_NAME = 'BSF Campus'

DOMAIN = 'koombook.lan'

STAFF_HOME_CARDS = [
    {
        'is_staff': True,
        'category': 'manage',
        'url': 'user_list',
        'title': _('Users'),
        'description': _('Create, remove or modify users.'),
        'fa': 'users',
    },
    {
        'is_staff': True,
        'category': 'manage',
        'url': 'server:power',
        'title': _('Stop/Restart'),
        'description': _('Stop or restart the server.'),
        'fa': 'power-off',
    },
    {
        'is_staff': True,
        'category': 'manage',
        'url': 'server:power',
        'title': _('Backups'),
        'description': _('Create, restore, download, upload backups.'),
        'fa': 'life-ring',
    },
]

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
