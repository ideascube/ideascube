# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0009_auto_20150728_0858'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='loan',
            options={'ordering': ('due_date', 'created_at')},
        ),
        migrations.RemoveField(
            model_name='loan',
            name='status',
        ),
        migrations.AddField(
            model_name='loan',
            name='returned_at',
            field=models.DateTimeField(default=None, null=True, verbose_name='Return time', blank=True),
        ),
    ]
