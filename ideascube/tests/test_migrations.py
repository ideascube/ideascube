from ideascube.tests.helpers import migration_test


@migration_test(
    migrate_from=[('ideascube', '0017_auto_20170117_1432')],
    migrate_to=[('ideascube', '0018_user_occupations')])
def test_renaming_some_occupations(migration):
    User = migration.old_apps.get_model('ideascube', 'User')
    User(serial='1').save()
    User(serial='2', current_occupation='student').save()
    User(serial='3', current_occupation='no_profession').save()
    User(serial='4', current_occupation='profit_profession').save()
    User(serial='5', current_occupation='whatever').save()
    User(serial='6', current_occupation='profit_profession').save()

    migration.run_migration()

    User = migration.new_apps.get_model('ideascube', 'User')
    users = User.objects.order_by('serial')
    assert users[0].serial == '1'
    assert users[0].current_occupation == ''
    assert users[1].serial == '2'
    assert users[1].current_occupation == 'student'
    assert users[2].serial == '3'
    assert users[2].current_occupation == 'unemployed'
    assert users[3].serial == '4'
    assert users[3].current_occupation == 'employee'
    assert users[4].serial == '5'
    assert users[4].current_occupation == 'whatever'
    assert users[5].serial == '6'
    assert users[5].current_occupation == 'employee'
