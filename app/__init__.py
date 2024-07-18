'''
Flask application factory module
'''
from flask import Flask
from peewee import SqliteDatabase
from config import config
from .models import sqlite_db


def create_app(config_name):
    '''
    Create and configure the Flask application.

    Args:
    config_name (str): The configuration to use.

    Returns:
    Flask: The configured Flask application.
    '''
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db = SqliteDatabase(app.config['DATABASE']['name'])
    sqlite_db.initialize(db)

    # pylint: disable=import-outside-toplevel
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    # pylint: enable=import-outside-toplevel

    return app
