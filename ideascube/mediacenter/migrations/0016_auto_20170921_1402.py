# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-21 14:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediacenter', '0015_auto_20170609_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='credits',
            field=models.CharField(blank=True, max_length=300, verbose_name='Authorship'),
        ),
        migrations.AlterField(
            model_name='document',
            name='summary',
            field=models.TextField(blank=True, verbose_name='summary'),
        ),
    ]
