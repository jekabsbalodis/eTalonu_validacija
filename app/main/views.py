'''
Main routes and view functions for the Flask application.
Includes theme toggling
'''
import duckdb
from flask import jsonify, redirect, render_template, request, session, url_for, current_app
from . import main


@main.get('/toggle-theme')
def toggle_theme():
    '''Toggle between light and dark themes'''
    current_theme = session.get('theme')
    if current_theme == 'dark':
        session['theme'] = 'light'
    else:
        session['theme'] = 'dark'
    return redirect(request.args.get('current_page') or '/')


@main.route('/', methods=['GET'])
def index():
    '''Render the start page of the app'''
    return render_template('index.jinja')


@main.route('/routes', methods=['GET'])
def routes():
    '''Render the page with statistics of most used routes'''
    return render_template('routes.jinja')


@main.route('/routes_data')
@main.route('/times', methods=['GET'])
def times():
    '''Render the page with statistics of hours when public transportation is used the most'''
    data_url = url_for('main.times_data')
    return render_template('time.jinja', data_url=data_url)


@main.get('/times_data')
def times_data():
    '''Get data for times page'''
    results = []

    with duckdb.connect(current_app.config['DATABASE']) as con:
        query = '''
            SELECT
                TMarsruts AS route,
                EXTRACT(hour FROM Laiks) AS hour,
                COUNT(*) AS count
            FROM
                validacijas
            GROUP BY
                route, hour
            ORDER BY
                route, hour;
            '''
        query_results = con.sql(query).fetchall()

    for route, hour, count in query_results:
        # Find existing route in results
        existing_route = next(
            (r for r in results if r['route'] == route), None)

        if existing_route:
            # If route exists, update its validations for the specific hour
            existing_route['validations'][int(hour)] = count
        else:
            # If route doesn't exist, create a new route entry with validations
            route_dict = {
                'route': route,
                'validations': {int(hour): count}
            }
            results.append(route_dict)

    # Ensure every route has validation counts for all 24 hours (default to 0)
    for route_dict in results:
        for hour in range(24):
            if hour not in route_dict['validations']:
                route_dict['validations'][hour] = 0

    # Return the results as JSON
    return jsonify(results)
