from ideascube.tests.helpers import migration_test


@migration_test(
    migrate_from=[('monitoring', '0005_auto_20161027_0801')],
    migrate_to=[('monitoring', '0006_unique_serial')]
)
def test_do_not_break_already_unique_serial(migration):
    Specimen = migration.old_apps.get_model('monitoring', 'Specimen')
    StockItem = migration.old_apps.get_model('monitoring', 'StockItem')

    stock_item = StockItem()
    stock_item.save()

    for i in range(5):
        specimen = Specimen(item_id=stock_item.id, barcode=str(i), serial=str(i))
        specimen.save()

    migration.run_migration()

    Specimen = migration.new_apps.get_model('monitoring', 'Specimen')
    specimens = Specimen.objects.order_by('barcode')
    assert specimens.count() == 5
    for specimen in specimens:
        assert specimen.barcode == specimen.serial


@migration_test(
    migrate_from=[('monitoring', '0005_auto_20161027_0801')],
    migrate_to=[('monitoring', '0006_unique_serial')]
)
def test_create_unique_serial(migration):
    Specimen = migration.old_apps.get_model('monitoring', 'Specimen')
    StockItem = migration.old_apps.get_model('monitoring', 'StockItem')

    stock_item = StockItem()
    stock_item.save()

    for i in range(5):
        specimen = Specimen(item_id=stock_item.id, barcode=str(i), serial='9')
        specimen.save()

    migration.run_migration()

    Specimen = migration.new_apps.get_model('monitoring', 'Specimen')
    specimens = Specimen.objects.order_by('barcode')
    assert specimens.count() == 5
    for specimen in specimens:
        assert specimen.serial.startswith('9')


@migration_test(
    migrate_from=[('monitoring', '0005_auto_20161027_0801')],
    migrate_to=[('monitoring', '0006_unique_serial')]
)
def test_migration_do_not_mix_between_unique_serial(migration):
    Specimen = migration.old_apps.get_model('monitoring', 'Specimen')
    StockItem = migration.old_apps.get_model('monitoring', 'StockItem')

    for i in range(5):
        stock_item = StockItem(name=str(i))
        stock_item.save()
        for j in range(5):
            specimen = Specimen(item_id=stock_item.id, barcode=str(i)+str(j), serial=str(i))
            specimen.save()

    migration.run_migration()

    Specimen = migration.new_apps.get_model('monitoring', 'Specimen')
    specimens = Specimen.objects.order_by('barcode')
    assert specimens.count() == 25
    for specimen in specimens:
        assert specimen.serial.startswith(specimen.item.name)

