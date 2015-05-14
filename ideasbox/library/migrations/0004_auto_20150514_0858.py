# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0003_auto_20150401_0925'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookspecimen',
            name='sp_file',
            field=models.FileField(upload_to=b'library/file', verbose_name='file', blank=True),
        ),
        migrations.AlterField(
            model_name='bookspecimen',
            name='serial',
            field=models.CharField(max_length=40, unique=True, null=True, verbose_name='serial'),
        ),
    ]
