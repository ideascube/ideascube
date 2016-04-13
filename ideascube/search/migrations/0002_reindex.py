# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from ideascube.search.utils import create_index_table

reindex = lambda *args: create_index_table(force=True)


class Migration(migrations.Migration):

    dependencies = [('search', '0001_initial')]

    operations = [
        migrations.RunPython(reindex, reindex),
    ]
