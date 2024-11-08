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


def get_time_range() -> tuple[date, date]:
    '''Get time range for the currently available data'''

    with duckdb.connect(current_app.config['DATABASE'], read_only=True) as con:
        time_range: tuple[date, date] = con.sql(
            TIME_RANGE_QUERY).fetchone()  # type: ignore
    return time_range


def render_page(template: str, data_url: str, form_url: str):
    '''Render the main pages'''

    time_range = get_time_range()
    form = DateSelectForm()
    start_date = time_range[1].replace(day=1)
    end_date = time_range[1]

    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data

    form.start_date.data = start_date
    form.end_date.data = end_date

    urls = (url_for(data_url, start_date=start_date, end_date=end_date),
            url_for(form_url),
            url_for(data_url))

    return render_template(template, urls=urls, form=form, time_range=time_range)


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


@main.route('/routes', methods=['GET', 'POST'])
def routes():
    '''Render the page with statistics of most used routes.'''

    return render_page('routes.jinja', 'data.routes_data', 'main.routes')


@main.route('/times', methods=['GET', 'POST'])
def times():
    '''Render the page with statistics of hours when public transportation is used the most.'''

    return render_page('times.jinja', 'data.times_data', 'main.times')
