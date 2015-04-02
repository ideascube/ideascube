# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('monitoring', '0006_entry_partner'),
    ]

    operations = [
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('due_date', models.DateField(default=datetime.date.today, verbose_name='Due date')),
                ('comments', models.CharField(max_length=500, verbose_name='Comments', blank=True)),
                ('by', models.ForeignKey(related_name='loans_made', to=settings.AUTH_USER_MODEL)),
                ('specimen', models.ForeignKey(to='monitoring.Specimen', unique=True)),
                ('user', models.ForeignKey(related_name='loans', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-due_date', '-created_at'),
            },
            bases=(models.Model,),
        ),
    ]
