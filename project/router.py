class DatabaseRouter:
    def db_for_read(self, model, **hints):
        # accounts, library 및 django 기본 시스템 앱들은 Supabase(default) 사용
        if model._meta.app_label in ['accounts', 'library', 'admin', 'auth', 'contenttypes', 'sessions', 'messages']:
            return 'default'
        return 'mysql'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in ['accounts', 'library', 'admin', 'auth', 'contenttypes', 'sessions', 'messages']:
            return 'default'
        return 'mysql'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in ['accounts', 'library', 'admin', 'auth', 'contenttypes', 'sessions', 'messages']:
            return db == 'default'
        return db == 'mysql'
