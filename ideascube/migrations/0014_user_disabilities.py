# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-29 13:51
from __future__ import unicode_literals

from django.db import migrations

from multiselectfield import MultiSelectField


class CommaSeparatedCharField(MultiSelectField):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('ideascube', '0013_auto_20161028_1044'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='disabilities',
            field=CommaSeparatedCharField(blank=True, choices=[('visual', 'Visual'), ('auditive', 'Auditive'), ('physical', 'Physical'), ('cognitive', 'Cognitive'), ('mental', 'Mental')], max_length=128, verbose_name='Disabilities'),
        ),
    ]
