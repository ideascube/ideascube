# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediacenter', '0006_auto_20160310_2005'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='package_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='package_id'),
        ),
    ]
