# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediacenter', '0003_auto_20160107_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='kind',
            field=models.CharField(choices=[('image', 'image'), ('audio', 'sound'), ('video', 'video'), ('pdf', 'pdf'), ('text', 'text'), ('epub', 'epub'), ('other', 'other')], max_length=5, default='other', verbose_name='type'),
        ),
    ]
