# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_auto_20150331_1606'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookSpecimenDigital',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('serial', models.CharField(max_length=40, unique=True, null=True, verbose_name='serial', blank=True)),
                ('remarks', models.TextField(verbose_name='remarks', blank=True)),
                ('book', models.ForeignKey(related_name='specimens_digital', to='library.Book')),
            ],
            options={
                'ordering': ['-modified_at'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
