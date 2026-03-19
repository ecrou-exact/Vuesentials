class Config:
    SECRET_KEY = 'SECRET_KEY_ENV_VAR_SET'
    
    FLASK_URL = '127.0.0.1'
    FLASK_PORT = 7009

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///vueEsential.sqlite"
    SESSION_TYPE = "sqlalchemy"
    SESSION_SQLALCHEMY_TABLE = "flask_sessions"
    # sqlite3 instance/vueEsential.sqlite
    @classmethod
    def init_app(cls, app):
        print('THIS APP IS IN DEBUG MODE. \
                YOU SHOULD NOT SEE THIS IN PRODUCTION.')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///vueEsential-test.sqlite"
    WTF_CSRF_ENABLED = False

    @classmethod
    def init_app(cls, app):
        print('THIS APP IS IN TESTING MODE.  \
                YOU SHOULD NOT SEE THIS IN PRODUCTION.')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# python backup.py -b              # create a new backup
# python backup.py -l              # list all available backups

# python restore.py -i             # Restore the latest backup
# python restore.py -l             # List all available backups
# python restore.py -r [filename]   # Restore a specific backup