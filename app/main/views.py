'''
Main routes and view functions for the Flask application.
Includes theme toggling.
'''
from datetime import date

import duckdb
from flask import (current_app, redirect, render_template, request, session,
                   url_for)

from app.main import main
from app.main.forms import DateSelectForm

TIME_RANGE_QUERY = '''
        SELECT
            date_trunc('day', MIN(Laiks)) AS min_time,
            date_trunc('day', MAX(Laiks)) AS max_time
        FROM
            validacijas;
        '''


def get_time_range() -> tuple[date]:
    '''Get time range for the currently available data'''

    with duckdb.connect(current_app.config['DATABASE'], read_only=True) as con:
        time_range: tuple[date] = con.sql(
            TIME_RANGE_QUERY).fetchone()  # type: ignore
    return time_range


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

    time_range = get_time_range()
    form = DateSelectForm()
    urls = (url_for('data.routes_data'), url_for('ajax.routes_ajax'))
    return render_template('routes.jinja', urls=urls, form=form, time_range=time_range)


@main.get('/times')
def times():
    '''Render the page with statistics of hours when public transportation is used the most.'''
    
    time_range = get_time_range()
    form = DateSelectForm()
    urls = (url_for('data.times_data'), url_for('ajax.times_ajax'))
    return render_template('time.jinja', urls=urls, form=form, time_range=time_range)
