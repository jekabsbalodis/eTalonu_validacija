'''
Ajax blueprint module for the Flask application.

Defines the ajax blueprint and imports views.

Responsible for view functions that respond to form post requests
'''
from flask import Blueprint

ajax = Blueprint('ajax', __name__)

from . import views  # pylint: disable=wrong-import-position
