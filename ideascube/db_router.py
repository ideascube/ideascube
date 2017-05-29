
_database_to_use = {
    ('search', 'search'): 'transient'
}


def get_database(app_label, model_name, default=None):
    return _database_to_use.get((app_label, model_name), default)


class DatabaseRouter(object):
    """
    A Database router.
    Some models do not need (and must not be backuped).
    So we route them to the transient base.
    """
    def db_for_read(self, model, **hints):
        """
        Return the database from which this model can be read,
        or None to use the default database.
        """
        return get_database(model._meta.app_label, model._meta.model_name)

    def db_for_write(self, model, **hints):
        """
        Return database for which this model can be write,
        or None to use the default database.
        """
        return get_database(model._meta.app_label, model._meta.model_name)

    def allow_relation(self, obj1, obj2, **hints):
        """Return whether a relation is allowed between these two models

        We only allow relations between models stored in the same database.
        """
        # I'm not sure of how to correctly implement this method.
        # It was the same for allow_migrate and I made it wrong.

        # However, there is no JOIN relation between two tables of two
        # different db for now. So it seems safe to me to simply allow relation
        # if the tables are in the same db.
        return get_database(obj1._meta.app_label, obj1._meta.model_name) \
            == get_database(obj2._meta.app_label, obj2._meta.model_name)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Allow migration only if the migration is applying to the right db.
        """
        db_to_use = get_database(app_label, model_name, default='default')
        if db_to_use != db:
            return False
        using = hints.get('using')
        if using:
            return using == db
        return True
