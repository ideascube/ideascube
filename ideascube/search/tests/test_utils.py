# -*- coding: utf-8 -*-
import pytest


pytestmark = pytest.mark.django_db

from ideascube.search.utils import create_index_table
from django.db import connections


def test_index_table_is_not_in_default_db():
    create_index_table(force=True)

    cursor = connections['default'].cursor()
    cursor.execute("SELECT count(*) FROM sqlite_master "
                   "WHERE type='table' AND name='idx';")
    count = cursor.fetchone()[0]
    assert count == 0

    cursor = connections['transient'].cursor()
    cursor.execute("SELECT count(*) FROM sqlite_master "
                   "WHERE type='table' AND name='idx';")
    count = cursor.fetchone()[0]
    assert count == 1
