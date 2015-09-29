# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0007_loan'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='status',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Status', choices=[(0, 'due'), (1, 'returned')]),
        ),
        migrations.AlterField(
            model_name='loan',
            name='specimen',
            field=models.OneToOneField(to='monitoring.Specimen'),
        ),
    ]
