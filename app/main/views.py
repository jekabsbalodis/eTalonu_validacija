'''
Main routes and view functions for the Flask application.
Includes theme toggling.
'''
from typing import TypedDict
import duckdb
from flask import jsonify, redirect, render_template, request, session, url_for, current_app

from app.main.forms import MonthSelectForm
from . import main


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
    # data_url = url_for('main.routes_data')
    with duckdb.connect(current_app.config['DATABASE']) as con:
        query: str = '''
            SELECT
                TMarsruts AS route,
                COUNT(*) AS count
            FROM
                validacijas
            GROUP BY
                TMarsruts
            ORDER BY
                count DESC
            '''
        query_results = con.sql(query).fetchall()
    return render_template('routes.jinja', results=query_results)


@main.get('/routes_data')
def routes_data():
    '''Get data for routes page.'''
    with duckdb.connect(current_app.config['DATABASE']) as con:
        query: str = '''
            SELECT
                TMarsruts AS route,
                COUNT(*) AS count
            FROM
                validacijas
            GROUP BY
                TMarsruts
            ORDER BY
                count DESC
            '''
        query_results = con.sql(query).fetchall()
    return jsonify(query_results)


@main.route('/times', methods=['GET', 'POST'])
def times():
    '''Render the page with statistics of hours when public transportation is used the most.'''
    form = MonthSelectForm()
    data_url = url_for('main.times_data')
    if form.validate_on_submit():
        start_date_tuple = (form.start_date.data.strftime(
            '%m'), form.start_date.data.strftime('%Y'))
        end_date_tuple = (form.end_date.data.strftime('%m'),
                          form.end_date.data.strftime('%Y'))
        data_url = url_for(
            'main.times_data',
            start_month=start_date_tuple[0],
            start_year=start_date_tuple[1],
            end_month=end_date_tuple[0],
            end_year=end_date_tuple[1])
    return render_template('time.jinja', data_url=data_url, form=form)


@main.get('/times_data')
def times_data():
    '''Get data for times page.'''

    class ResultsDict(TypedDict):
        '''Define model for the data to hold validations for each route and hour.'''
        route: str
        validations: dict[int, int]

    requested_date = request.args

    with duckdb.connect(current_app.config['DATABASE']) as con:
        max_month = con.sql('''
                        SELECT
                            month(max(Laiks)),
                            year(max(Laiks))
                        FROM
                            validacijas;
                        ''').fetchone()
        print(max_month)
        test = con.sql('''
                    WITH LastMonth AS (
                        SELECT
                            EXTRACT(MONTH FROM MAX(Laiks)) AS max_m,
                            EXTRACT(YEAR FROM MAX(Laiks)) AS max_y
                        FROM
                            validacijas
                    )
                    SELECT
                        date_trunc('day', MIN(Laiks)) AS min_time,
                        date_trunc('day', MAX(Laiks)) AS max_time
                    FROM
                        validacijas, LastMonth
                    WHERE
                        EXTRACT(MONTH FROM Laiks) = LastMonth.max_m AND
                        EXTRACT(YEAR FROM Laiks) = LastMonth.max_y;
                    ''').fetchone()
        print(test[1])
        query = '''
            SELECT
                TMarsruts AS route,
                EXTRACT(hour FROM Laiks) AS hour,
                COUNT(*) AS count
            FROM
                validacijas
            WHERE
                EXTRACT(month FROM Laiks)={} AND,
                EXTRACT(year FROM Laiks)={}
            GROUP BY
                route, hour
            ORDER BY
                route, hour;
            '''
        if requested_date:
            query_results = con.sql(query.format(
                requested_date['start_month'], requested_date['start_year'])).fetchall()
        else:
            query_results = con.sql(query.format(
                *max_month)).fetchall()  # type: ignore

    results: list[ResultsDict] = []

    for route, hour, count in query_results:
        # Check if route dict already exists
        existing_route = next(
            (r for r in results if r['route'] == route), None)

        if existing_route:
            # Update validations for the specific hour
            existing_route['validations'][int(hour)] = int(count)
        else:
            # Create a new route dict with validations
            route_dict: ResultsDict = {
                'route': route,
                'validations': {int(hour): int(count)}
            }
            results.append(route_dict)

    # Ensure every route has validation counts for all 24 hours (default to 0)
    for route_dict in results:
        for hour in range(24):
            if hour not in route_dict['validations']:
                route_dict['validations'][hour] = 0

    return jsonify(results)
