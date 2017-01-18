# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations


def do_upgrade(apps, schema_editor):
    User = apps.get_model('ideascube', 'User')
    db_alias = schema_editor.connection.alias
    all_users = User.objects.using(db_alias)

    users = all_users.filter(current_occupation='no_profession')
    users.update(current_occupation='unemployed')

    users = all_users.filter(current_occupation='profit_profession')
    users.update(current_occupation='employee')


class Migration(migrations.Migration):

    dependencies = [
        ('ideascube', '0017_auto_20170117_1432'),
    ]

    operations = [
        migrations.RunPython(
            do_upgrade, migrations.RunPython.noop, hints={'using': 'default'}),
    ]
