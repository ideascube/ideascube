# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from ideascube.search.utils import create_index_table


class CreateSearchModel(migrations.CreateModel):
    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # Don't run the parent method, we create the table our own way
        model = to_state.apps.get_model(app_label, self.name)
        if self.allow_migrate_model(schema_editor.connection.alias, model):
            create_index_table()


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        CreateSearchModel(
            name='Search',
            fields=[],
            options={
                'db_table': 'idx',
                'managed': False,
            },
        ),
    ]
