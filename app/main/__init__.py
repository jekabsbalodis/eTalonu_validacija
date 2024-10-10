'''
Main blueprint module for the Flask application.

Defines the main blueprint and imports views and error handlers.
'''
from flask import Blueprint

main = Blueprint('main', __name__)

from . import errors, views  # pylint: disable=wrong-import-position
