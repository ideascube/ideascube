"""Ideasbox Aurore in Paris Clichy, France"""
from .idb_fra import *  # noqa
from django.utils.translation import ugettext_lazy as _

IDEASCUBE_NAME = u"Aurore"
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
        'id': 'wikipedia.old',
    },
    {
        'id': 'khanacademy',
    },
    {
        'id': 'gutenberg.old',
    },
    {
        'id': 'vikidia.old',
    },
]
