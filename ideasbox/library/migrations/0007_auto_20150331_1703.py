# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0006_auto_20150331_1701'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookspecimendigital',
            name='serial',
            field=models.CharField(default=b'livre', max_length=40, null=True, verbose_name='serial', blank=True),
            preserve_default=True,
        ),
    ]
