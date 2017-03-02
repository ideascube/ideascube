# -*- coding: utf-8 -*-
from django.db import migrations
from django.utils.html import escape


def escape_summary(app, schema_editor):
    Document = app.get_model('mediacenter', 'Document')
    db_alias = schema_editor.connection.alias
    for document in Document.objects.using(db_alias).all():
        document.summary = "<p>{}</p>".format(escape(document.summary))
        document.save()


class Migration(migrations.Migration):

    dependencies = [
        ('mediacenter', '0013_auto_20170323_1525'),
    ]

    operations = [
        migrations.RunPython(escape_summary, migrations.RunPython.noop)
    ]
