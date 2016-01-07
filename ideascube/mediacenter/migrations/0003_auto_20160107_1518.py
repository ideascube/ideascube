# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediacenter', '0002_auto_20151129_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='original',
            field=models.FileField(upload_to=b'mediacenter/document', max_length=10240, verbose_name='original'),
        ),
        migrations.AlterField(
            model_name='document',
            name='preview',
            field=models.ImageField(upload_to=b'mediacenter/preview', max_length=10240, verbose_name='preview', blank=True),
        ),
    ]
