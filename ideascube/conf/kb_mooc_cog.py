"""KoomBook conf"""
from .kb import *  # noqa

LANGUAGE_CODE = 'fr'
IDEASCUBE_NAME = 'UNIVERSITE RDC'
HOME_CARDS = HOME_CARDS + [  # pragma: no flakes
    {
        'id': 'koombookedu',
    },
]
