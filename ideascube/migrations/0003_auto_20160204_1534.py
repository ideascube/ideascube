# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import ideascube.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ideascube', '0002_auto_20151129_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='fa_level',
            field=ideascube.fields.CommaSeparatedCharField(blank=True, choices=[('u', 'Understood'), ('w', 'Written'), ('s', 'Spoken'), ('r', 'Read')], verbose_name='Persian knowledge', max_length=32),
        ),
    ]
