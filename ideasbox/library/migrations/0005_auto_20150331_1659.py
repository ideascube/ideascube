# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0004_auto_20150331_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookspecimendigital',
            name='serial',
            field=models.CharField(null=True, default=0, max_length=40, blank=True, unique=True, verbose_name='serial'),
            preserve_default=True,
        ),
    ]
