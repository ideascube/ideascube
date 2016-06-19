# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.core.management import call_command


def reindex(*args):
    call_command('reindex')


class Migration(migrations.Migration):

    dependencies = [('search', '0001_initial')]

    operations = [
        migrations.RunPython(reindex, reindex),
    ]
