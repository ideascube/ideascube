import os

from .base import *  # noqa


try:
    os.makedirs(os.path.join(STORAGE_ROOT, 'main'))
except OSError:
    pass

CATALOG_CACHE_ROOT = os.path.join(STORAGE_ROOT, 'catalog')
