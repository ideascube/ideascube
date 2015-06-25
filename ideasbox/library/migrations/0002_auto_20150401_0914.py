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
            field=models.PositiveSmallIntegerField(verbose_name='section', choices=[(1, 'digital'), (2, 'children - cartoons'), (3, 'children - novels'), (10, 'children - poetry'), (11, 'children - theatre'), (4, 'children - documentary'), (5, 'children - comics'), (6, 'adults - novels'), (12, 'adults - poetry'), (13, 'adults - theatre'), (7, 'adults - documentary'), (8, 'adults - comics'), (9, 'game'), (99, 'other')]),
            preserve_default=True,
        ),
    ]
