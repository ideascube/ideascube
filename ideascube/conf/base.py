# -*- coding: utf-8 -*-
"""Django settings for ideascube project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

import os
import subprocess

from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PROJECT_DIR = os.path.join(BASE_DIR, 'ideascube')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '16exrv_@=2(za=oj$tj+l_^v#sbt83!=t#wz$s+1udfa04#vz!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('DEBUG', True))

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['.ideasbox.lan.', 'localhost']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ideascube',
    'ideascube.serveradmin',
    'ideascube.blog',
    'ideascube.library',
    'ideascube.search',
    'ideascube.mediacenter',
    'ideascube.monitoring',
    'taggit',
    'django_countries',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.request",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "ideascube.context_processors.settings",
    "ideascube.context_processors.version",
)

ROOT_URLCONF = 'ideascube.urls'

WSGI_APPLICATION = 'ideascube.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)
LOGIN_REDIRECT_URL = 'index'
LOGIN_URL = 'login'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = os.environ.get('TIME_ZONE', 'UTC')

USE_I18N = True

USE_L10N = True

USE_TZ = True

AVAILABLE_LANGUAGES = (
    ('en', 'English'),
    ('fr', u'Français'),
    ('ar', u'العربية'),
    ('am', u'አማርኛ'),
    ('so', u'Af-Soomaali'),
    ('sw', u'Swahili'),
    ('bm', u'Bambara'),
)

# Those will be added to django.locale.LANG_INFO.
EXTRA_LANG_INFO = {
    'bm': {
        'bidi': False,
        'name': 'Bambara',
        'code': 'bm',
        'name_local': 'Bambara'
    },
    'am': {
        'bidi': False,
        'name': 'Amharic',
        'code': 'am',
        'name_local': u'አማርኛ'
    },
    'so': {
        'bidi': False,
        'name': 'Somali',
        'code': 'am',
        'name_local': u'Af-Soomaali'
    }
}

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'ideascube', 'locale'),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'


# Ideas Box specifics
STORAGE_ROOT = os.environ.get('STORAGE_ROOT',
                              os.path.join(BASE_DIR, 'storage'))

# Loaded relatively to STORAGE_ROOT on settings.py
BACKUPED_ROOT = None
MEDIA_ROOT = None
STATIC_ROOT = None
DATABASES = None

AUTH_USER_MODEL = 'ideascube.User'
IDEASCUBE_NAME = 'debugbox'
IDEASCUBE_PLACE_NAME = _('the camp')
IDEASCUBE_BODY_ID = 'ideasbox'

LOAN_DURATION = 0  # In days.

DOMAIN = 'ideasbox.lan'
WIKIPEDIA_URL = 'http://wikipedia.{domain}'.format(domain=DOMAIN)
KHANACADEMY_URL = 'http://khanacademy.{domain}'.format(domain=DOMAIN)

# Fields to be used in the entry export. This export is supposed to be
# anonymized, so no personal data like name.
MONITORING_ENTRY_EXPORT_FIELDS = ['birth_year', 'gender']

USERS_LIST_EXTRA_FIELDS = ['serial']

USER_INDEX_FIELDS = ['short_name', 'full_name', 'serial']

USER_FORM_FIELDS = (
    (_('Basic informations'), ['serial', 'short_name', 'full_name']),
    (_('Language skills'), ['ar_level', 'en_level']),
)

ENTRY_ACTIVITY_CHOICES = [
]

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
        'url': 'monitoring:entry',
        'title': _('Entries'),
        'description': _('Manage user entries.'),
        'fa': 'sign-in',
    },
    {
        'is_staff': True,
        'category': 'manage',
        'url': 'monitoring:stock',
        'title': _('Stock'),
        'description': _('Manage stock.'),
        'fa': 'barcode',
    },
    {
        'is_staff': True,
        'category': 'manage',
        'url': 'monitoring:loan',
        'title': _('Loans'),
        'description': _('Manage loans.'),
        'fa': 'exchange',
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
        'url': 'server:backup',
        'title': _('Backups'),
        'description': _('Create, restore, download, upload backups.'),
        'fa': 'life-ring',
    },
    {
        'is_staff': True,
        'category': 'manage',
        'url': 'server:wifi',
        'title': _('Wi-Fi'),
        'description': _('Manage Wi-Fi connections.'),
        'fa': 'wifi',
    },
]

HOME_CARDS = STAFF_HOME_CARDS + [
    {
        'id': 'blog',
    },
    {
        'id': 'library',
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

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

SERVICES = [
    {'name': 'ideascube', 'description': _('Ideascube web server')},
    {'name': 'nginx', 'description': _('Global proxy')},
    {
        'name': 'kalite',
        'description': _('Daemon which provides KhanAcademy on lan'),
    },
    {'name': 'kiwix',
        'description': _('Daemon which provides Wikipedia on lan')},
    {'name': 'ntp', 'description': _('Net time protocol')},
    {'name': 'ssh',
        'description': _('Daemon used for distant connexion to server')},
]


SESSION_COOKIE_AGE = 60 * 60  # Members must be logged out after one hour
BACKUP_FORMAT = 'zip'  # One of 'zip', 'tar', 'bztar', 'gztar'
