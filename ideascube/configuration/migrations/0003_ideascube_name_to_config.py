from django.conf import settings
from django.db import migrations

from ideascube.configuration import set_config


def do_migrate(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    Configuration = apps.get_model('configuration', 'Configuration')
    configs = Configuration.objects.using(db_alias)

    User = apps.get_model('ideascube', 'User')
    users = User.objects.using(db_alias)

    try:
        configs.get(namespace='server', key='site-name')

    except Configuration.DoesNotExist:
        # No value was set in the DB
        ideascube_name = getattr(settings, 'IDEASCUBE_NAME', '')

        if ideascube_name:
            # Use the value set in the settings file
            system_user = users.get_system_user()
            set_config('server', 'site-name', ideascube_name, system_user)


class Migration(migrations.Migration):

    dependencies = [
        ('ideascube', '0009_add_a_system_user'),
        ('configuration', '0002_settings_to_configuration'),
    ]

    operations = [
        migrations.RunPython(do_migrate, hints={'using': 'default'}),
    ]
