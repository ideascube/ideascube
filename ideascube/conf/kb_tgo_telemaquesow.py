"""KoomBook conf"""
from .kb import *  # pragma: no flakes

LANGUAGE_CODE = 'fr'
IDEASCUBE_NAME = 'kb78-TelemaqueSow'
CUSTOM_CARDS = [
    {
        # Must be one of create, discover, info, learn, manage, read
        'category': 'info',
        'url': 'http://mail.koombook.lan',
        'title': 'Webmail',
        'description': 'Ecrire et lire des e-mails',
        # The name of a Font Awesome glyph
        'fa': 'envelope-o',
        # True if the card should only be visible by the staff
        'is_staff': False
    },
]