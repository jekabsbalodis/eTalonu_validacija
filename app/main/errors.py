'''View functions for various errors'''
from flask import render_template
from . import main


@main.app_errorhandler(401)
def unauthorized(e):
    '''Function for unauthorized access'''
    return 401

@main.app_errorhandler(403)
def forbidden(e):
    '''Function for forbidden access'''
    return 403


@main.app_errorhandler(404)
def page_not_found(e):
    '''Function for non-existent page'''
    return 404


@main.app_errorhandler(500)
def internal_server_error(e):
    '''Function for internal server error'''
    return 500
