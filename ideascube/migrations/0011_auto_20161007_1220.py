# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-07 12:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ideascube', '0010_auto_20160901_0801'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True, verbose_name='creation date'),
        ),
        migrations.AlterField(
            model_name='user',
            name='modified_at',
            field=models.DateTimeField(
                auto_now=True, verbose_name='modification date'),
        ),
        migrations.AlterField(
            model_name='user',
            name='serial',
            field=models.CharField(
                max_length=40, unique=True, verbose_name='identifier'),
        ),
    ]
