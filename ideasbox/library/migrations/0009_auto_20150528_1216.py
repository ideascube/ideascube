# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0008_auto_20150528_1133'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookspecimen',
            name='is_digital',
        ),
        migrations.AddField(
            model_name='bookspecimen',
            name='digital',
            field=models.BooleanField(default=False, verbose_name='digital'),
            preserve_default=True,
        ),
    ]
