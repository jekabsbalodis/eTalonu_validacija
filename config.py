import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE = {
        'name': 'data-dev.sqlite',
        'engine': 'peewee.SqliteDatabase',
    }


class TestingConfig(Config):
    TESTING = True
    DATABASE = DATABASE = {
        'name': ':memory:',
        'engine': 'peewee.SqliteDatabase',
    }


class ProductionConfig(Config):
    DATABASE = DATABASE = {
        'name': 'data.sqlite',
        'engine': 'peewee.SqliteDatabase',
    }


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
