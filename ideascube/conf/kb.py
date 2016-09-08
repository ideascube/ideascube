from .base import *  # noqa

ALLOWED_HOSTS = ['.koombook.lan.', 'localhost', '127.0.0.1']
TIME_ZONE = None
DOMAIN = 'koombook.lan'
BACKUP_FORMAT = 'gztar'
IDEASCUBE_BOX_TYPE = 'koombook'
STAFF_HOME_CARDS = [c for c in STAFF_HOME_CARDS
                    if c['url'] in ['user_list', 'server:power',
                                    'server:backup', 'server:wifi']]

HOME_CARDS = STAFF_HOME_CARDS + [
    {
        'id': 'blog',
    },
    {
        'id': 'mediacenter',
    },
    {
        'id': 'bsfcampus',
    },
    {
        'id': 'wikipedia',
        'languages': ['en', 'wo', 'fr']
    },
    {
        'id': 'khanacademy',
    },
    {
        'id': 'wikisource',
        'languages': ['fr', 'en']
    },
    {
        'id': 'vikidia',
        'languages': ['fr']
    },
    {
        'id': 'gutenberg',
        'lang': 'fr',
    },
    {
        'id': 'cest-pas-sorcier',
    },
    {
        'id': 'ted',
        'sessions': [
            ('tedxgeneva2014.fr', 'Geneva 2014'),
            ('tedxlausanne2012.fr', 'Lausanne 2012'),
            ('tedxlausanne2013.fr', 'Lausanne 2013'),
            ('tedxlausanne2014.fr', 'Lausanne 2014'),
        ]
    },
    {
        'id': 'software',
    },
    {
        'id': 'ubuntudoc',
        'languages': ['fr']
    },
]
