import os

from .base import *  # pragma: no flakes


DEBUG = True
ALLOWED_HOSTS += ['localhost', '127.0.0.1']  # pragma: no flakes

try:
    os.makedirs(os.path.join(STORAGE_ROOT, 'main'))  # pragma: no flakes
except OSError:
    pass

CATALOG_CACHE_ROOT = os.path.join(STORAGE_ROOT, 'catalog')  # pragma: no flakes
