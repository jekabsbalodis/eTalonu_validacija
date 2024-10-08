'''
Main routes and view functions for the Flask application.
Includes theme toggling.
'''
from flask import redirect, render_template, request, session, url_for

from app.main import main
from app.main.forms import TimeSelectForm


@main.get('/toggle-theme')
def toggle_theme():
    '''Toggle between light and dark themes.'''
    current_theme = session.get('theme')
    if current_theme == 'dark':
        session['theme'] = 'light'
    else:
        session['theme'] = 'dark'
    return redirect(request.args.get('current_page') or '/')


@main.get('/')
def index():
    '''Render the start page of the app.'''
    return render_template('index.jinja')


@main.get('/routes')
def routes():
    '''Render the page with statistics of most used routes.'''
    data_url = url_for('data.routes_data')
    return render_template('routes.jinja', data_url=data_url)


@main.get('/times')
def times():
    '''Render the page with statistics of hours when public transportation is used the most.'''
    form = TimeSelectForm()
    data_url = url_for('data.times_data')
    return render_template('time.jinja', data_url=data_url, form=form)
