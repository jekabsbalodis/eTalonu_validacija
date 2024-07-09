from flask import Flask
from flask_bootstrap import Bootstrap5
from peewee import SqliteDatabase
from config import config
from .models import sqlite_db

bootstrap = Bootstrap5()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db = SqliteDatabase(app.config['DATABASE']['name'])
    sqlite_db.initialize(db)

    # pylint: disable=wrong-import-position
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    # pylint: enable=wrong-import-position

    return app
