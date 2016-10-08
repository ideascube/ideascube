# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-07 12:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0002_auto_20160322_1824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True, verbose_name='creation date'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='modified_at',
            field=models.DateTimeField(
                auto_now=True, verbose_name='modification date'),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True, verbose_name='creation date'),
        ),
        migrations.AlterField(
            model_name='inventory',
            name='modified_at',
            field=models.DateTimeField(
                auto_now=True, verbose_name='modification date'),
        ),
        migrations.AlterField(
            model_name='loan',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True, verbose_name='creation date'),
        ),
        migrations.AlterField(
            model_name='loan',
            name='modified_at',
            field=models.DateTimeField(
                auto_now=True, verbose_name='modification date'),
        ),
        migrations.AlterField(
            model_name='specimen',
            name='count',
            field=models.IntegerField(default=1, verbose_name='quantity'),
        ),
        migrations.AlterField(
            model_name='stockitem',
            name='module',
            field=models.CharField(
                choices=[
                    ('cinema', 'Cinema'), ('library', 'Library'),
                    ('digital', 'Multimedia'), ('admin', 'Administration'),
                    ('other', 'Other')
                ], max_length=20, verbose_name='module'),
        ),
    ]