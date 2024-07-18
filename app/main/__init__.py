'''
Main blueprint module for the Flask application.

Defines the main blueprint and imports views and error handlers.
'''
from flask import Blueprint

main = Blueprint('main', __name__)

# pylint: disable=wrong-import-position
from . import views, errors
# pylint: enable=wrong-import-position
