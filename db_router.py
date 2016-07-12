class DatabaseRouter(object):
    """
    A Database router.
    Some models do not need (and must not be backuped).
    Those models will (must) have a _dbname class attribute set to 'transiant'.
    This attribute will be use as database name.
    """
    def db_for_read(self, model, **hints):
        """
        If the model as a _dbname set, use it as db for read
        """
        return getattr(model, '_dbname', None)

    def db_for_write(self, model, **hints):
        """
        If the model as a _dbname set, use it as db for read
        """
        return getattr(model, '_dbname', None)

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both object are in the same database.
        """
        return getattr(obj1, '_dbname', None) == getattr(obj2, '_dbname', None)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        All database need to be migrated.
        """
        return True
