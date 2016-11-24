# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def add_user(apps, *args):
    # The apps.get_model() method returns us a 'fake' model with a
    # default manager and the 'save' method is not overwritten
    # and the user is not indexed at creation.
    # This is not a problem here as we have post-migrate hook who reindex
    # everything at end of migration. Moreover, it is better has we do not
    # have to care about if the 'transient' db is existing or not when doing
    # this migration.
    User = apps.get_model('ideascube', 'User')
    User(serial='__system__', full_name='System', password='!!').save()


class Migration(migrations.Migration):

    dependencies = [
        ('ideascube', '0008_user_sdb_level'),
        ('search', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_user, None, hints={'using': 'default'}),
    ]
