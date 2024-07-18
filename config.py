'''Configuration module for the application.'''
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    '''Base configuration'''
    SECRET_KEY = os.environ.get('SECRET_KEY')

    @staticmethod
    def init_app(app):
        '''Initialize app'''


class DevelopmentConfig(Config):
    '''Development configuration'''
    DEBUG = True
    DATABASE = {
        'name': 'data-dev.sqlite',
        'engine': 'peewee.SqliteDatabase',
    }


class TestingConfig(Config):
    '''Testing configuration'''
    TESTING = True
    DATABASE = {
        'name': ':memory:',
        'engine': 'peewee.SqliteDatabase',
    }


class ProductionConfig(Config):
    '''Production configuration'''
    DATABASE = {
        'name': 'data.sqlite',
        'engine': 'peewee.SqliteDatabase',
    }


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
