'''Configuration module for the application.'''
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    '''Base configuration'''
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SESSION_COOKIE_SAMESITE = 'Strict'

    @staticmethod
    def init_app(app):
        '''Initialize app'''


class DevelopmentConfig(Config):
    '''Development configuration'''
    DEBUG = True
    DATABASE = 'data-dev.duckdb'


class TestingConfig(Config):
    '''Testing configuration'''
    TESTING = True
    DATABASE = ''


class ProductionConfig(Config):
    '''Production configuration'''
    DATABASE = 'data.duckdb'
    SESSION_COOKIE_SECURE = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
