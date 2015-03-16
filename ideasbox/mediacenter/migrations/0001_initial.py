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
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=100, verbose_name='title')),
                ('summary', models.TextField(verbose_name='summary')),
                ('lang', models.CharField(blank=True, max_length=10, verbose_name='Language', choices=[(b'en', b'English'), (b'fr', 'Fran\xe7ais'), (b'ar', '\u0627\u0644\u0639\u0631\u0628\u064a\u0629')])),
                ('original', models.FileField(upload_to=b'mediacenter/document', verbose_name='original')),
                ('preview', models.ImageField(upload_to=b'mediacenter/preview', verbose_name='preview', blank=True)),
                ('credits', models.CharField(max_length=300, verbose_name='credit')),
                ('kind', models.CharField(default=b'other', max_length=5, verbose_name='type', choices=[(b'image', 'image'), (b'audio', 'sound'), (b'video', 'video'), (b'pdf', 'pdf'), (b'text', 'text'), (b'other', 'other')])),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
