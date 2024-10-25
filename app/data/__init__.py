'''
Data blueprint module for the Flask application.

Defines the data blueprint and imports views.

Responsible for returning data to initial page load and afterwards when user changes data selection
'''
from flask import Blueprint

data = Blueprint('data', __name__)

from . import views  # pylint: disable=wrong-import-position
