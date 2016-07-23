# -*- coding: utf-8 -*-
"""Bardarash in Kurdistan"""
from .azraq import *  # noqa
from django.utils.translation import ugettext_lazy as _

IDEASCUBE_NAME = u"Bardarash"

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
        'id': 'khanacademy',
    },
    {
        'id': 'wikipedia',
        'languages': ['en', 'ar']
    },
    {
        'id': 'wiktionary',
        'languages': ['en', 'ar']
    },
    {
        'id': 'wikiversity',
        'languages': ['en', 'ar']
    },
    {
        'id': 'ted',
        'sessions': [
            ('tedbusiness.en', 'Business'),
            ('teddesign.en', 'Design'),
            ('tedentertainment.en', 'Entertainment'),
            ('tedglobalissues.en', 'Global Issues'),
            ('tedscience.en', 'Science'),
            ('tedtechnology.en', 'Technology'),
        ]
    },
    {
        'id': 'gutenberg',
        'lang': 'mul',
    },
    {
        'id': 'maps',
        'maps': [
            ('World', 'world.map'),
            ('Iraq', 'iraq.map'),
        ]
    }
]
