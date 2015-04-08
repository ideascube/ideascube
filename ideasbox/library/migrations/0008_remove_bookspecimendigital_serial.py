# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0007_auto_20150331_1703'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookspecimendigital',
            name='serial',
        ),
    ]
