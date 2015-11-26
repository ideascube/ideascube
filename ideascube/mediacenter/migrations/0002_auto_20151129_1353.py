# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediacenter', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='lang',
            field=models.CharField(blank=True, max_length=10, verbose_name='Language', choices=[(b'en', b'English'), (b'fr', 'Fran\xe7ais'), (b'ar', '\u0627\u0644\u0639\u0631\u0628\u064a\u0629'), (b'sw', 'Swahili'), (b'bm', 'Bambara')]),
        ),
    ]
