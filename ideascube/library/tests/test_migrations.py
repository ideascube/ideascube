from ideascube.tests.helpers import migration_test

section_int_to_name = {
    8: 'adults-comics',
    7: 'adults-documentary',
    6: 'adults-novels',
    12: 'adults-poetry',
    13: 'adults-theatre',
    2: 'children-cartoons',
    5: 'children-comics',
    4: 'children-documentary',
    3: 'children-novels',
    10: 'children-poetry',
    11: 'children-theatre',
    1: 'digital',
    9: 'game',
    99: 'other'
}


@migration_test(migrate_from=[('library', '0009_auto_20161027_0801')],
                migrate_to=[('library', '0010_section_type')])
def test_section_migration_change_from_int_to_string(migration):
    Book = migration.old_apps.get_model('library', 'Book')
    for i in range(14):
        #There is no section 0, use 99 instead
        i = i or 99
        Book.objects.create(name=str(i), section=i)

    migration.run_migration()

    Book = migration.new_apps.get_model('library', 'Book')
    for book in Book.objects.all():
        old_section = int(book.name)
        assert book.section == section_int_to_name[old_section]
