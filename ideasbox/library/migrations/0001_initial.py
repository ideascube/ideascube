# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('isbn', models.CharField(max_length=40, unique=True, null=True, blank=True)),
                ('authors', models.CharField(max_length=300, verbose_name='authors', blank=True)),
                ('serie', models.CharField(max_length=300, verbose_name='serie', blank=True)),
                ('title', models.CharField(max_length=300, verbose_name='title')),
                ('subtitle', models.CharField(max_length=300, verbose_name='subtitle', blank=True)),
                ('summary', models.TextField(verbose_name='summary', blank=True)),
                ('publisher', models.CharField(max_length=100, verbose_name='publisher', blank=True)),
                ('section', models.PositiveSmallIntegerField(verbose_name='section', choices=[(1, 'digital'), (2, 'children - cartoons'), (3, 'children - novels'), (4, 'children - documentary'), (5, 'children - comics'), (6, 'adults - novels'), (7, 'adults - documentary'), (8, 'adults - comics'), (9, 'game'), (99, 'other')])),
                ('location', models.CharField(max_length=300, verbose_name='location', blank=True)),
                ('lang', models.CharField(max_length=10, verbose_name='Language', choices=[(b'en', b'English'), (b'fr', 'Fran\xe7ais'), (b'ar', '\u0627\u0644\u0639\u0631\u0628\u064a\u0629')])),
                ('cover', models.ImageField(upload_to=b'library/cover', verbose_name='cover', blank=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'ordering': ['title'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BookSpecimen',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('serial', models.CharField(unique=True, max_length=40, verbose_name='serial')),
                ('remarks', models.TextField(verbose_name='remarks', blank=True)),
                ('book', models.ForeignKey(related_name='specimens', to='library.Book')),
            ],
            options={
                'ordering': ['-modified_at'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
