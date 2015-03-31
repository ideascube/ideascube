# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='section',
            field=models.PositiveSmallIntegerField(verbose_name='section', choices=[(1, 'children - cartoons'), (2, 'children - novels'), (3, 'children - documentary'), (4, 'children - comics'), (5, 'adults - novels'), (6, 'adults - documentary'), (7, 'adults - comics'), (8, 'game'), (99, 'other')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bookspecimen',
            name='serial',
            field=models.CharField(max_length=40, unique=True, null=True, verbose_name='serial', blank=True),
            preserve_default=True,
        ),
    ]
