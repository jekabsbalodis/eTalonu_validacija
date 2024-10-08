'''
Main routes and view functions for the Flask application.
Includes theme toggling.
'''
from typing import TypedDict
import duckdb
from flask import jsonify, redirect, render_template, request, session, url_for, current_app
from app.main.forms import TimeSelectForm
from app.main import main


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


@main.get('/times')
def times():
    '''Render the page with statistics of hours when public transportation is used the most.'''
    form = TimeSelectForm()
    data_url = url_for('main.times_data')
    return render_template('time.jinja', data_url=data_url, form=form)


@main.route('/times_data', methods=['GET', 'POST'])
def times_data():
    '''Get data for times page.'''

    class DatasetDict(TypedDict):
        '''Define model for the dataset dict.'''
        label: str
        data: list[int]

    class ResultsDict(TypedDict):
        '''Define model for the data to hold validations for each route and hour.'''
        labels: list[int]
        datasets: list[DatasetDict]

    form = TimeSelectForm()

    with duckdb.connect(current_app.config['DATABASE']) as con:
        last_month = con.sql('''
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
        query = '''
            SELECT
                'all',
                EXTRACT(hour FROM Laiks) AS hour,
                COUNT(*) AS count
            FROM
                validacijas
            WHERE
                Laiks BETWEEN '{} 00:00:00' AND '{} 23:59:59'
            GROUP BY
                 hour
            ORDER BY
                hour;
            '''
        if request.method == 'POST' and form.validate_on_submit():
            start_date_tuple = (form.start_date.data.strftime(
                '%m'), form.start_date.data.strftime('%Y'))
            end_date_tuple = (form.end_date.data.strftime('%m'),
                              form.end_date.data.strftime('%Y'))

            query_results = con.sql(query.format()).fetchall()
        else:
            query_results = con.sql(query.format(
                *last_month)).fetchall()

    results: ResultsDict = {'labels': [],
                            'datasets': []}
    print(query_results)

    for route, hour, count in query_results:
        # Add the route label to the datasets if it doesn't exist
        if route not in [dataset["label"] for dataset in results["datasets"]]:
            results["datasets"].append(
                {"label": route, "data": [0] * 24})  # Initialize with 24 zeros

        # Find the dataset for the current route
        dataset = [dataset for dataset in results["datasets"]
                   if dataset["label"] == route][0]

        # Add the validation to the dataset's data list at the corresponding hour index
        dataset["data"][hour] = count

        # Add the hour to the labels list if it doesn't exist
        if hour not in results["labels"]:
            results["labels"].append(hour)

    results["labels"].sort()

    # # Ensure every route has validation counts for all 24 hours (default to 0)
    # for route_dict in results:
    #     for hour in range(24):
    #         if hour not in route_dict['validations']:
    #             route_dict['validations'][hour] = 0

    return jsonify(results)
