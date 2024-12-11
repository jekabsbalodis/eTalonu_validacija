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
        pass  # pylint: disable=unnecessary-pass


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
    DATABASE_NAME = os.environ.get('DATABASE_NAME')
    MD_TOKEN = os.environ.get('MD_TOKEN')
    DATABASE = f'md:{DATABASE_NAME}?token={MD_TOKEN}'
    SESSION_COOKIE_SECURE = True


class DockerConfig(ProductionConfig):
    '''Configuration for Docker deployment'''

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging  # pylint: disable=import-outside-toplevel
        from logging import StreamHandler  # pylint: disable=import-outside-toplevel
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,

    'default': DevelopmentConfig
}
