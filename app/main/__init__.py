'''
Main blueprint module for the Flask application.

Defines the main blueprint and imports views and error handlers.
'''
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors  # pylint: disable=wrong-import-position
