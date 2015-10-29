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

IDEASCUBE_NAME = 'Coeur de Forêt'

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
        'category': 'create',
        'url': 'http://appinventor.koombook.lan',
        'title': 'App Inventor',
        'description': 'Créer vos propres applications Android',
        'img': 'img/app-inventor.jpeg',
    },
    {
        'category': 'read',
        'url': 'http://vikidia.koombook.lan',
        'title': 'Vikidia',
        'description': 'Parcourir l\'encyclopedie libre pour les jeunes',
        'img': '/img/Vikidia.png',
    },
    {
        'category': 'learn',
        'url': 'http://cpassorcier.koombook.lan',
        'title': 'C\'est pas sorcier',
        'description': 'Le magazine de vulgarisation scientifique ',
        'img': '/img/cpassorcier.png',
    },
]

IDEASCUBE_BODY_ID = 'koombook'
