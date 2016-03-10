# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediacenter', '0005_auto_20160211_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='kind',
            field=models.CharField(max_length=5, default='other', verbose_name='type', choices=[('image', 'image'), ('audio', 'sound'), ('video', 'video'), ('pdf', 'pdf'), ('text', 'text'), ('epub', 'epub'), ('software', 'software'), ('other', 'other')]),
        ),
    ]
