# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0003_auto_20160211_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='cover',
            field=models.ImageField(blank=True, verbose_name='cover', upload_to='library/cover'),
        ),
        migrations.AlterField(
            model_name='book',
            name='lang',
            field=models.CharField(verbose_name='Language', choices=[('am', 'አማርኛ'), ('ar', 'العربية'), ('bm', 'Bambara'), ('de', 'Deutsch'), ('el', 'Ελληνικά'), ('en', 'English'), ('fa', 'فارسی'), ('fr', 'Français'), ('it', 'Italiano'), ('ps', 'پښتو'), ('rn', 'Kirundi'), ('so', 'Af-Soomaali'), ('sw', 'Swahili'), ('ti', 'ትግርኛ'), ('ur', 'اردو')], max_length=10),
        ),
        migrations.AlterField(
            model_name='bookspecimen',
            name='file',
            field=models.FileField(blank=True, verbose_name='digital file', upload_to='library/digital'),
        ),
    ]
