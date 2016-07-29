# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, connections


def migrate(*_):
    cursor_default = connections['default'].cursor()
    cursor_default.execute("DROP TABLE IF EXISTS idx")


class Migration(migrations.Migration):

    dependencies = [('search', '0001_initial')]

    operations = [
        migrations.RunPython(migrate),
    ]
