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
        {
        'category': 'read',
        'url': 'http://wikisource.koombook.lan',
        'title': 'Wikisource',
        'description': 'Bibliothèque de textes libres et gratuits',
        'img': '/img/wikisource.png',
    },
    {
        'category': 'learn',
        'url': 'http://bsfcampus.koombook.lan',
        'title': 'Bsf Campus',
        'description': 'Renforcer les capacités des bibliothèques',
        'img': '/img/bsfcampus.png',
    },
    {
        'category': 'read',
        'url': 'http://gutenberg.koombook.lan',
        'title': 'Projet Gutenberg',
        'description': 'Livre numérique à lire en ligne ou a télécharger',
        'img': '/img/gutenberg.jpeg',
    },
    {
        'category': 'learn',
        'url': 'http://ted.koombook.lan',
        'title': 'TED Vidéos',
        'description': 'Une série vidéo de conférences organisées ',
        'img': '/img/ted.jpg',
    },
    {
        'category': 'learn',
        'url': 'http://ubuntudoc.koombook.lan',
        'title': 'Ubuntu documentation',
        'description': 'La documentation du célèbre système d\'exploitation Ubuntu',
        'img': '/img/ubuntudoc.jpeg',
    },
    {
        'category': 'create',
        'url': 'http://software.koombook.lan',
        'title': 'Logiciels Windows',
        'description': 'télécharger des applications Windows libres et gratuites',
        'img': '/img/windows.jpeg',
    },
]

IDEASCUBE_BODY_ID = 'koombook'
