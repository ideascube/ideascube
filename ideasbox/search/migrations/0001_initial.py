# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ideasbox.search.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Search',
            fields=[
                ('rowid', models.IntegerField(serialize=False, primary_key=True)),
                ('model', models.CharField(max_length=64)),
                ('model_id', models.IntegerField()),
                ('public', models.BooleanField(default=True)),
                ('text', ideasbox.search.models.SearchField()),
            ],
            options={
                'db_table': 'idx',
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
