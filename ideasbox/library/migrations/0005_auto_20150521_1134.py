# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0004_auto_20150514_0858'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bookspecimen',
            old_name='sp_file',
            new_name='spfile',
        ),
    ]
