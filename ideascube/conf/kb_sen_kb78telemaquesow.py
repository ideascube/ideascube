"""KoomBook conf"""
from .kb import *  # pragma: no flakes

LANGUAGE_CODE = 'fr'
CUSTOM_CARDS = [
    {
        'category': 'info',
        'url': 'http://mail.koombook.lan',
        'title': 'Webmail',
        'description': 'Ecrire et lire des e-mails',
        'fa': 'envelope-o',
        'is_staff': False
    },
]