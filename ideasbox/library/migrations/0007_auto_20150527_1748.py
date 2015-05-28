# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0006_auto_20150521_1207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookspecimen',
            name='serial',
            field=models.CharField(max_length=40, unique=True, null=True, verbose_name='serial', blank=True),
            preserve_default=True,
        ),
    ]
