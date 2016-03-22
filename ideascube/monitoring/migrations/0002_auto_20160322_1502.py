# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='specimen',
            options={'ordering': ('barcode',)},
        ),
        migrations.AlterField(
            model_name='entry',
            name='module',
            field=models.CharField(choices=[('cinema', 'Cinema'), ('library', 'Library'), ('digital', 'Multimedia')], max_length=20),
        ),
        migrations.AlterField(
            model_name='stockitem',
            name='module',
            field=models.CharField(choices=[('cinema', 'Cinema'), ('library', 'Library'), ('digital', 'Multimedia'), ('admin', 'Administration'), ('other', 'Other')], max_length=20),
        ),
    ]
