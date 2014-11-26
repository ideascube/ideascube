"""
Django settings for ideasbox project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os

from django.utils.translation import ugettext_lazy as _


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, 'ideasbox')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '16exrv_@=2(za=oj$tj+l_^v#sbt83!=t#wz$s+1udfa04#vz!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'serveradmin',
    'ideasbox',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'ideasbox.urls'

WSGI_APPLICATION = 'ideasbox.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)
LOGIN_REDIRECT_URL = 'index'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'


# Ideas Box specifics
try:
    IDEASBOX_ID = os.environ['IDEASBOX_ID']
except KeyError:
    if DEBUG:
        IDEASBOX_ID = 'debugbox'
    else:
        raise
try:
    STORAGE_ROOT = os.environ['DATASTORAGE']
except KeyError:
    if DEBUG:
        try:
            os.makedirs('storage/main')
        except OSError:
            pass
        STORAGE_ROOT = os.path.join(BASE_DIR, 'storage')
    else:
        raise
MEDIA_ROOT = os.path.join(STORAGE_ROOT, 'main')
AUTH_USER_MODEL = os.environ.get('AUTH_USER_MODEL', 'ideasbox.DefaultUser')

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(MEDIA_ROOT, 'default.sqlite'),
    }
}

SERVICES = [
    {'name': 'apache2', 'sum': _('Daemon which provide web content')},
    {'name': 'bind9', 'sum': _('Daemon which provide local DNS')},
    {'name': 'kalite', 'sum': _('Daemon which provide KhanAcademy on lan')},
    {'name': 'kiwix', 'sum': _('Daemon which provide Wikipedia on lan')},
    {'name': 'ntp', 'sum': _('Net time protocol')},
    {'name': 'ssh', 'sum': _('Daemon used for distant connexion to server')},
]
