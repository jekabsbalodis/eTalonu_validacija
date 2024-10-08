'''
Flask application factory module
'''
from flask import Flask

from config import config


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

    from .main import \
        main as main_blueprint  # pylint: disable=import-outside-toplevel
    app.register_blueprint(main_blueprint)
    from .data import \
        data as data_blueprint  # pylint: disable=import-outside-toplevel
    app.register_blueprint(data_blueprint)

    return app
