'''
Validation blueprint module for the Flask application.

Defines the validation blueprint and imports views.
'''
from flask import Blueprint

validation = Blueprint('validation', __name__)

from . import views  # pylint: disable=wrong-import-position
