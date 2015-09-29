# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0008_auto_20150727_1940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='specimen',
            field=models.ForeignKey(to='monitoring.Specimen'),
        ),
    ]
