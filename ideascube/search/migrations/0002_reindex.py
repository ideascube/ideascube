# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, connections
from ideascube.search.utils import reindex_content


def update_reindex(*args):
    cursor_default = connections['default'].cursor()
    cursor_default.execute("DROP TABLE IF EXISTS idx")
    reindex_content()


class Migration(migrations.Migration):

    dependencies = [('search', '0001_initial')]

    operations = [
        migrations.RunPython(update_reindex, None),
    ]
