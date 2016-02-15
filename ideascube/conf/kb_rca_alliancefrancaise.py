# -*- coding: utf-8 -*-
"""KoomBook conf"""
from .kb import *  # noqa

LANGUAGE_CODE = 'fr'
IDEASCUBE_NAME = 'Alliance française de Bangui'

# Disable BSF Campus for now
HOME_CARDS = [card for card in HOME_CARDS if card.get('id') != 'bsfcampus']
