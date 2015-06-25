# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_auto_20150401_0914'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='location',
        ),
        migrations.AddField(
            model_name='bookspecimen',
            name='location',
            field=models.CharField(max_length=300, verbose_name='location', blank=True),
            preserve_default=True,
        ),
    ]
