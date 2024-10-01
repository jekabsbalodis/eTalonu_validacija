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

    # pylint: disable=import-outside-toplevel
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    # pylint: enable=import-outside-toplevel

    return app
