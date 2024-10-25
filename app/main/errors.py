'''
Error handlers for the main blueprint
'''
from flask import render_template

from . import main


@main.app_errorhandler(404)
def page_not_found(e):
    '''Handle 404 Not Found errors'''
    return render_template('404.jinja'), 404


@main.app_errorhandler(405)
def method_not_allowed(e):
    '''Handle 405 Method Not Allowed errors'''
    return render_template('405.jinja'), 405


@main.app_errorhandler(500)
def internal_server_error(e):
    '''Handle 500 Internal Server errors'''
    return render_template('500.jinja'), 500
