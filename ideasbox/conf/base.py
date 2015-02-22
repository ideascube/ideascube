# -*- coding: utf-8 -*-
"""Django settings for ideasbox project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os

from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PROJECT_DIR = os.path.join(BASE_DIR, 'ideasbox')

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
    'ideasbox',
    'ideasbox.serveradmin',
    'ideasbox.blog',
    'ideasbox.library',
    'ideasbox.search',
    'ideasbox.mediacenter',
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
    "ideasbox.context_processors.settings"
)

ROOT_URLCONF = 'ideasbox.urls'

WSGI_APPLICATION = 'ideasbox.wsgi.application'

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
)

SUPPORTED_LANGUAGES = os.environ.get('SUPPORTED_LANGUAGES', 'fr en ar').split()
LANGUAGES = []
for code, label in AVAILABLE_LANGUAGES:
    if code in SUPPORTED_LANGUAGES:
        LANGUAGES.append((code, label))

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'


# Ideas Box specifics
STORAGE_ROOT = os.environ.get('STORAGE_ROOT',
                              os.path.join(BASE_DIR, 'storage'))

BACKUPED_ROOT = os.path.join(STORAGE_ROOT, 'main')

MEDIA_ROOT = os.path.join(BACKUPED_ROOT, 'media')
STATIC_ROOT = os.path.join(STORAGE_ROOT, 'static')

AUTH_USER_MODEL = 'ideasbox.DefaultUser'
IDEASBOX_NAME = 'debugbox'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BACKUPED_ROOT, 'default.sqlite'),
    }
}

SERVICES = [
    {'name': 'ideasbox', 'description': _('Ideasbox web server')},
    {'name': 'nginx', 'description': _('Global proxy')},
    {'name': 'bind9', 'description': _('Local DNS')},
    {'name': 'kalite',
        'description': _('Daemon which provides KhanAcademy on lan')},
    {'name': 'kiwix',
        'description': _('Daemon which provides Wikipedia on lan')},
    {'name': 'ntp', 'description': _('Net time protocol')},
    {'name': 'ssh',
        'description': _('Daemon used for distant connexion to server')},
]
