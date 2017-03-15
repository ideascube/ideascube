# -*- coding: utf-8 -*-
from django.db import migrations
from django.utils.html import escape


def escape_summary(app, schema_editor):
    Content = app.get_model('blog', 'Content')
    db_alias = schema_editor.connection.alias
    for content in Content.objects.using(db_alias).all():
        content.summary = "<p>{}</p>".format(escape(content.summary))
        content.save()


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_auto_20161027_0801'),
    ]

    operations = [
        migrations.RunPython(escape_summary, migrations.RunPython.noop)
    ]
