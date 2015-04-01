# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0004_auto_20150330_0922'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='activity',
            field=models.CharField(max_length=200, blank=True),
            preserve_default=True,
        ),
    ]
