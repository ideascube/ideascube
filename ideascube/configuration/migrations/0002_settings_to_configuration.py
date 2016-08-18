from __future__ import unicode_literals

from django.db import migrations

from ideascube.configuration import set_config


def do_migrate(apps, schema_editor):
    Setting = apps.get_model('ideascube', 'Setting')
    db_alias = schema_editor.connection.alias

    for setting in Setting.objects.using(db_alias).all():
        set_config(
            setting.namespace, setting.key, setting.value, setting.actor)


class Migration(migrations.Migration):

    dependencies = [
        ('ideascube', '0005_setting'),
        ('ideascube', '0009_add_a_system_user'),
        ('configuration', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(do_migrate),
    ]
