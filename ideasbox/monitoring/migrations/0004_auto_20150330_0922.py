# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0003_auto_20150324_1806'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='inventoryspecimen',
            unique_together=set([('inventory', 'specimen')]),
        ),
    ]
