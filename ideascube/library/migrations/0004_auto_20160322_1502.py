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
            model_name='bookspecimen',
            name='file',
            field=models.FileField(blank=True, verbose_name='digital file', upload_to='library/digital'),
        ),
    ]
