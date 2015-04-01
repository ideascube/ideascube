# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0005_entry_activity'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='partner',
            field=models.CharField(max_length=200, blank=True),
            preserve_default=True,
        ),
    ]
