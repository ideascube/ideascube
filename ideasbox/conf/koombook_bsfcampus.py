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