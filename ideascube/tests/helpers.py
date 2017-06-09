import pytest


def migration_test(migrate_from, migrate_to):
    no_migration_skip = pytest.mark.skipif(pytest.config.getoption("--nomigrations"),
                                           reason="skipping due to --nomigrations"
                                          )
    parametrize_migration = pytest.mark.parametrize('migration',
                         [(migrate_from,
                           migrate_to
                         )],
                         indirect=['migration'])
    def wrapper(function):
        f = pytest.mark.migrations(function)
        f = parametrize_migration(f)
        f = no_migration_skip(f)
        return f
    return wrapper
