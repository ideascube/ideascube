# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0002_auto_20150324_0703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='module',
            field=models.CharField(max_length=20, choices=[(b'cinema', 'Cinema'), (b'library', 'Library'), (b'digital', 'Multimedia')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='stockitem',
            name='module',
            field=models.CharField(max_length=20, choices=[(b'cinema', 'Cinema'), (b'library', 'Library'), (b'digital', 'Multimedia'), (b'admin', 'Administration'), (b'other', 'Other')]),
            preserve_default=True,
        ),
    ]
