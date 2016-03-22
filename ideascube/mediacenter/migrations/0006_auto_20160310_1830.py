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
            name='lang',
            field=models.CharField(choices=[('am', 'አማርኛ'), ('ar', 'العربية'), ('bm', 'Bambara'), ('de', 'Deutsch'), ('el', 'Ελληνικά'), ('en', 'English'), ('fa', 'فارسی'), ('fr', 'Français'), ('it', 'Italiano'), ('ps', 'پښتو'), ('rn', 'Kirundi'), ('so', 'Af-Soomaali'), ('sw', 'Swahili'), ('ti', 'ትግርኛ'), ('ur', 'اردو')], max_length=10, verbose_name='Language', blank=True),
        ),
    ]
