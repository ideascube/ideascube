# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.db import migrations


def add_user(*args):
    User = get_user_model()
    User(serial='__system__', full_name='System', password='!!').save()


class Migration(migrations.Migration):

    dependencies = [
        ('ideascube', '0008_user_sdb_level'),
        ('search', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_user, None),
    ]
