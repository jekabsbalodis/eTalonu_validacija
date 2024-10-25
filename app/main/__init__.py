'''
Main blueprint module for the Flask application.

Defines the main blueprint and imports views and error handlers.

Responsible for providing view functions for the main pages -
the pages user can browse through clicking on navigation links
'''
from flask import Blueprint

main = Blueprint('main', __name__)

from . import errors, views  # pylint: disable=wrong-import-position
