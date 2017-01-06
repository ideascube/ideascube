import os

from .base import *  # pragma: no flakes


try:
    os.makedirs(os.path.join(STORAGE_ROOT, 'main'))  # pragma: no flakes
except OSError:
    pass

CATALOG_CACHE_ROOT = os.path.join(STORAGE_ROOT, 'catalog')  # pragma: no flakes
