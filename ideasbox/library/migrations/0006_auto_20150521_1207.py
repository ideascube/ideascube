# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0005_auto_20150521_1134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookspecimen',
            name='serial',
            field=models.CharField(unique=True, max_length=40, verbose_name='serial', blank=True),
        ),
    ]
