# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediacenter', '0005_auto_20160211_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='kind',
            field=models.CharField(default='other', verbose_name='type', choices=[('image', 'image'), ('audio', 'sound'), ('video', 'video'), ('pdf', 'pdf'), ('text', 'text'), ('epub', 'epub'), ('app', 'app'), ('other', 'other')], max_length=5),
        ),
        migrations.AlterField(
            model_name='document',
            name='lang',
            field=models.CharField(blank=True, verbose_name='Language', choices=[('am', 'አማርኛ'), ('ar', 'العربية'), ('bm', 'Bambara'), ('de', 'Deutsch'), ('el', 'Ελληνικά'), ('en', 'English'), ('fa', 'فارسی'), ('fr', 'Français'), ('it', 'Italiano'), ('ps', 'پښتو'), ('rn', 'Kirundi'), ('so', 'Af-Soomaali'), ('sw', 'Swahili'), ('ti', 'ትግርኛ'), ('ur', 'اردو')], max_length=10),
        ),
        migrations.AlterField(
            model_name='document',
            name='original',
            field=models.FileField(upload_to='mediacenter/document', verbose_name='original', max_length=10240),
        ),
        migrations.AlterField(
            model_name='document',
            name='preview',
            field=models.ImageField(blank=True, verbose_name='preview', max_length=10240, upload_to='mediacenter/preview'),
        ),
    ]
