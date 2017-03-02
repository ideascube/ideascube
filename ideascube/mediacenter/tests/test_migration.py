from ideascube.tests.helpers import migration_test

@migration_test(
    migrate_from=[
        ('mediacenter', '0013_auto_20170323_1525')
    ], migrate_to=[('mediacenter', '0014_escape_summary')])
def test_migration_summary_should_be_safe(migration):
    Document = migration.old_apps.get_model('mediacenter', 'Document')

    document_1 = Document(title="document1", summary="A text")
    document_1.save()
    document_2 = Document(title="document2", summary="</div><script>alert('boo');</script>")
    document_2.save()

    migration.run_migration()

    Document = migration.new_apps.get_model('mediacenter', 'Document')

    documents = Document.objects.order_by('title')

    document = documents[0]
    assert document.summary == "<p>A text</p>"

    document = documents[1]
    assert document.summary == "<p>&lt;/div&gt;&lt;script&gt;alert(&#39;boo&#39;);&lt;/script&gt;</p>"

