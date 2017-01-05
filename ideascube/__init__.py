import sys

if sys.version_info.major != 3:
    sys.exit('ERROR: Ideascube only works with Python 3')


VERSION = (0, 18, 0)

__version__ = ".".join(map(str, VERSION))
