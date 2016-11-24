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


@migration_test(
    migrate_from=[
        ('library', '0007_auto_20161007_1220'),
        ('monitoring', '0004_auto_20161007_1240'),
        ('taggit', '0002_auto_20150616_2121'),
    ], migrate_to=[('library', '0008_library_stock')])
def test_library_to_monitoring_with_duplicated_data(migration):
    Book = migration.old_apps.get_model('library', 'Book')
    BookSpecimen = migration.old_apps.get_model('library', 'BookSpecimen')
    StockItem = migration.old_apps.get_model('monitoring', 'StockItem')
    Specimen = migration.old_apps.get_model('monitoring', 'Specimen')

    # Keep for later
    old_item_ids = []
    old_specimen_ids = []

    # First, a Book without BookSpecimen
    Book(section=10, title='Les blagues à Toto').save()

    # Next, a Book with 2 BookSpecimens
    book = Book(section=99, title='A book which was not in the stock')
    book.save()
    BookSpecimen(serial='1234', book_id=book.id).save()
    BookSpecimen(serial='2345', book_id=book.id).save()

    # Next, a Book with 2 BookSpecimens, the first of which has a Specimen
    book = Book(
        section=13, title='Testing Django Applications',
        subtitle='Volume 1364: Migrations')
    book.save()
    BookSpecimen(serial='3456', book_id=book.id).save()
    BookSpecimen(serial='4567', book_id=book.id).save()

    item = StockItem(name='testing django apps 1364')
    item.save()
    old_item_ids.append(item.id)
    specimen = Specimen(barcode='3456', item_id=item.id)
    specimen.save()
    old_specimen_ids.append(specimen.id)

    # Next, a Book with 2 BookSpecimens, the second of which has a Specimen
    book = Book(
        section=13, title='Testing Django Applications',
        subtitle='Volume 1365: Migrations Again')
    book.save()
    BookSpecimen(serial='5678', book_id=book.id).save()
    BookSpecimen(serial='6789', book_id=book.id).save()

    item = StockItem(name='testing django apps 1365')
    item.save()
    old_item_ids.append(item.id)
    specimen = Specimen(barcode='6789', item_id=item.id)
    specimen.save()
    old_specimen_ids.append(specimen.id)

    # Next, a Book with 2 BookSpecimens, both of which have a Specimen
    book = Book(
        section=13, title='Testing Django Applications',
        subtitle='Volume 1366: Migrations Forever')
    book.save()
    BookSpecimen(serial='7890', book_id=book.id).save()
    BookSpecimen(serial='8901', book_id=book.id).save()

    item = StockItem(name='testing django apps 1366')
    item.save()
    old_item_ids.append(item.id)
    specimen = Specimen(barcode='7890', item_id=item.id)
    specimen.save()
    old_specimen_ids.append(specimen.id)
    specimen = Specimen(barcode='8901', item_id=item.id)
    specimen.save()
    old_specimen_ids.append(specimen.id)

    migration.run_migration()

    Book = migration.new_apps.get_model('library', 'Book')
    BookSpecimen = migration.new_apps.get_model('library', 'BookSpecimen')
    StockItem = migration.new_apps.get_model('monitoring', 'StockItem')
    Specimen = migration.new_apps.get_model('monitoring', 'Specimen')

    assert Book.objects.count() == 5
    assert BookSpecimen.objects.count() == 8
    assert StockItem.objects.count() == 5
    assert Specimen.objects.count() == 8

    books = Book.objects.order_by('name', 'subtitle')
    bookspecimens = BookSpecimen.objects.order_by('item__name', 'barcode')
    items = StockItem.objects.order_by('name', 'book__subtitle')
    specimens = Specimen.objects.order_by('item__name', 'barcode')

    # First, the Book without BookSpecimen
    book = books[1]
    assert book.name == 'Les blagues à Toto'
    assert book.module == 'library'
    assert book.specimens.count() == 0

    item = items[1]
    assert item.id not in old_item_ids
    assert item.book.id == book.id
    assert item.specimens.count() == 0

    # Next, the Book with 2 BookSpecimens
    book = books[0]
    assert book.name == 'A book which was not in the stock'
    assert book.module == 'library'

    item = items[0]
    assert item.id not in old_item_ids
    assert item.book.id == book.id
    assert item.specimens.count() == 2

    bookspecimen = bookspecimens[0]
    assert bookspecimen.barcode == '1234'
    assert bookspecimen.serial is None
    assert bookspecimen.item.book.id == book.id

    specimen = specimens[0]
    assert specimen.id not in old_specimen_ids
    assert specimen.bookspecimen.id == bookspecimen.id
    assert specimen.item.id == item.id

    bookspecimen = bookspecimens[1]
    assert bookspecimen.barcode == '2345'
    assert bookspecimen.serial is None
    assert bookspecimen.item.book.id == book.id

    specimen = specimens[1]
    assert specimen.id not in old_specimen_ids
    assert specimen.bookspecimen.id == bookspecimen.id
    assert specimen.item.id == item.id

    # Next, the Book with 2 BookSpecimens, the first of which has a Specimen
    book = books[2]
    assert book.name == 'Testing Django Applications'
    assert book.subtitle == 'Volume 1364: Migrations'
    assert book.module == 'library'

    item = items[2]
    assert item.id in old_item_ids
    assert item.book.id == book.id
    assert item.specimens.count() == 2

    bookspecimen = bookspecimens[2]
    assert bookspecimen.barcode == '3456'
    assert bookspecimen.serial is None
    assert bookspecimen.item.book.id == book.id

    specimen = specimens[2]
    assert specimen.id in old_specimen_ids
    assert specimen.bookspecimen.id == bookspecimen.id
    assert specimen.item.id == item.id

    bookspecimen = bookspecimens[3]
    assert bookspecimen.barcode == '4567'
    assert bookspecimen.serial is None
    assert bookspecimen.item.book.id == book.id

    specimen = specimens[3]
    assert specimen.id not in old_specimen_ids
    assert specimen.bookspecimen.id == bookspecimen.id
    assert specimen.item.id == item.id

    # Next, a Book with 2 BookSpecimens, the second of which has a Specimen
    book = books[3]
    assert book.name == 'Testing Django Applications'
    assert book.subtitle == 'Volume 1365: Migrations Again'
    assert book.module == 'library'

    item = items[3]
    assert item.id in old_item_ids
    assert item.book.id == book.id
    assert item.specimens.count() == 2

    bookspecimen = bookspecimens[4]
    assert bookspecimen.barcode == '5678'
    assert bookspecimen.serial is None
    assert bookspecimen.item.book.id == book.id

    specimen = specimens[4]
    assert specimen.id not in old_specimen_ids
    assert specimen.bookspecimen.id == bookspecimen.id
    assert specimen.item.id == item.id

    bookspecimen = bookspecimens[5]
    assert bookspecimen.barcode == '6789'
    assert bookspecimen.serial is None
    assert bookspecimen.item.book.id == book.id

    specimen = specimens[5]
    assert specimen.id in old_specimen_ids
    assert specimen.bookspecimen.id == bookspecimen.id
    assert specimen.item.id == item.id

    # Next, a Book with 2 BookSpecimens, both of which have a Specimen
    book = books[4]
    assert book.name == 'Testing Django Applications'
    assert book.subtitle == 'Volume 1366: Migrations Forever'
    assert book.module == 'library'

    item = items[4]
    assert item.id in old_item_ids
    assert item.book.id == book.id
    assert item.specimens.count() == 2

    bookspecimen = bookspecimens[6]
    assert bookspecimen.barcode == '7890'
    assert bookspecimen.serial is None
    assert bookspecimen.item.book.id == book.id

    specimen = specimens[6]
    assert specimen.id in old_specimen_ids
    assert specimen.bookspecimen.id == bookspecimen.id
    assert specimen.item.id == item.id

    bookspecimen = bookspecimens[7]
    assert bookspecimen.barcode == '8901'
    assert bookspecimen.serial is None
    assert bookspecimen.item.book.id == book.id

    specimen = specimens[7]
    assert specimen.id in old_specimen_ids
    assert specimen.bookspecimen.id == bookspecimen.id
    assert specimen.item.id == item.id


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
