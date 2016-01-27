# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20151129_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='content',
            name='image',
            field=models.ImageField(blank=True, upload_to='blog/image', verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='content',
            name='lang',
            field=models.CharField(default='en', max_length=10, choices=[('en', 'English'), ('fr', 'Français'), ('ar', 'العربية'), ('am', 'አማርኛ'), ('so', 'Af-Soomaali'), ('sw', 'Swahili'), ('bm', 'Bambara')], verbose_name='Language'),
        ),
    ]
