# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=100, verbose_name='title')),
                ('author_text', models.CharField(max_length=300, verbose_name='author text', blank=True)),
                ('summary', models.CharField(max_length=300, verbose_name='summary')),
                ('image', models.ImageField(upload_to=b'blog/image', verbose_name='image', blank=True)),
                ('text', models.TextField(verbose_name='text')),
                ('published_at', models.DateTimeField(verbose_name='publication date')),
                ('status', models.PositiveSmallIntegerField(default=1, verbose_name='Status', choices=[(1, 'draft'), (2, 'published'), (3, 'deleted')])),
                ('lang', models.CharField(default=b'en', max_length=10, verbose_name='Language', choices=[(b'en', b'English'), (b'fr', 'Fran\xe7ais'), (b'ar', '\u0627\u0644\u0639\u0631\u0628\u064a\u0629')])),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
