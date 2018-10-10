from .idb import *  # pragma: no flakes

CUSTOM_CARDS = [
    {
        # Must be one of create, discover, info, learn, manage, read
        'category': 'create',
        'url': 'http://etherpad.ideasbox.lan',
        'title': 'Etherpad',
        'description': 'A collaborative text editor',
        # The name of a Font Awesome glyph
        'fa': 'font',
        # True if the card should only be visible by the staff
        'is_staff': False
    },
    {
        # Must be one of create, discover, info, learn, manage, read
        'category': 'learn',
        'url': 'http://moodle.ideasbox.lan',
        'title': 'Moodle',
        'description': 'Online courses',
        # The name of a Font Awesome glyph
        'fa': 'graduation-cap',
        # True if the card should only be visible by the staff
        'is_staff': False
    },
]
