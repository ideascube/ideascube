# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediacenter', '0006_auto_20160310_2005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='kind',
            field=models.CharField(choices=[('image', 'image'), ('audio', 'sound'), ('video', 'video'), ('pdf', 'pdf'), ('text', 'text'), ('epub', 'epub'), ('app', 'app'), ('other', 'other')], default='other', max_length=5, verbose_name='type'),
        ),
    ]
