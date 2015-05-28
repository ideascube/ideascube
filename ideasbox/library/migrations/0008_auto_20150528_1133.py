# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0007_auto_20150527_1748'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bookspecimen',
            old_name='spfile',
            new_name='specimenfile',
        ),
        migrations.AddField(
            model_name='bookspecimen',
            name='is_digital',
            field=models.BooleanField(default=False, verbose_name='type'),
            preserve_default=True,
        ),
    ]
