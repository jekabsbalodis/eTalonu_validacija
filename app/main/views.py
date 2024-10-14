'''
Main routes and view functions for the Flask application.
Includes theme toggling.
'''
from flask import redirect, render_template, request, session, url_for

from app.main import main
from app.main.forms import DateSelectForm


def get_selected_date(data_route: str):
    '''Function to extract start_date and end_date from DateSelectForm used in various places'''
    form = DateSelectForm()
    if form.validate_on_submit():
        data_url = url_for(
            data_route, start_date=form.start_date.data, end_date=form.end_date.data)
    else:
        data_url = url_for(data_route)
    return form, data_url


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
    form, data_url = get_selected_date('data.routes_data')
    return render_template('routes.jinja', data_url=data_url, form=form)


@main.route('/times', methods=['GET', 'POST'])
def times():
    '''Render the page with statistics of hours when public transportation is used the most.'''
    form, data_url = get_selected_date('data.times_data')
    return render_template('time.jinja', data_url=data_url, form=form)
