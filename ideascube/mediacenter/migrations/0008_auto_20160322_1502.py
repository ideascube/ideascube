# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediacenter', '0007_auto_20160322_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='original',
            field=models.FileField(upload_to='mediacenter/document', verbose_name='original', max_length=10240),
        ),
        migrations.AlterField(
            model_name='document',
            name='preview',
            field=models.ImageField(upload_to='mediacenter/preview', blank=True, verbose_name='preview', max_length=10240),
        ),
    ]
