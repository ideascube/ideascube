# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-18 10:38
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models

import ideascube.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('namespace', models.CharField(max_length=40)),
                ('key', models.CharField(max_length=40)),
                ('value', ideascube.models.JSONField()),
                ('date', models.DateTimeField(auto_now=True)),
                ('actor', models.ForeignKey(
                    on_delete=models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]