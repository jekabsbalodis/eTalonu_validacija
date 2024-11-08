'''
Data routes and view functions for the Flask app.
Includes routes that provide data for the corresponding main functions.
'''
from datetime import date, datetime
from typing import TypedDict

import duckdb
from flask import current_app, jsonify, request

from app.data import data


class RouteDataDict(TypedDict):
    '''Define model for the data to hold validations for each route and hour.'''

    label: str
    data: list[int]


class ResultsDict(TypedDict):
    '''Define model for the dict containing
    all the results that will be passed to template for rendering.'''

    labels: list[int | str]
    datasets: list[RouteDataDict]


LAST_MONTH_QUERY: str = '''
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
        '''

POPULAR_ROUTES_QUERY: str = '''
        SELECT
            TMarsruts AS route,
            COUNT(*) AS count
        FROM
            validacijas
        WHERE
            Laiks BETWEEN '{} 00:00:00' AND '{} 23:59:59'
        GROUP BY
            TMarsruts
        ORDER BY
            count DESC;
        '''

VALIDATIONS_BY_HOUR_QUERY: str = '''
        SELECT
            TMarsruts AS route,
            EXTRACT(hour FROM Laiks) AS hour,
            COUNT(*) AS count
        FROM
            validacijas
        WHERE
            Laiks BETWEEN '{} 00:00:00' AND '{} 23:59:59'
        GROUP BY
            route, hour
        ORDER BY
            hour;
        '''


def get_query_results(query: str, start_date: date | None = None, end_date: date | None = None):
    '''Function to get database records.'''

    with duckdb.connect(current_app.config['DATABASE'], read_only=True) as con:
        last_month: tuple[date, date] = con.sql(
            LAST_MONTH_QUERY).fetchone()  # type: ignore

        if start_date is not None and end_date is not None:
            query_results = con.sql(query.format(start_date, end_date)).df()
        else:
            query_results = con.sql(query.format(*last_month)).df()
    return query_results


def get_dates() -> tuple[date | None, date | None]:  # date range to be precise
    '''Function to get user defined start and end date.'''

    start_str = request.args.get('start_date')
    end_str = request.args.get('end_date')
    start_date, end_date = None, None

    if start_str and end_str:
        try:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    return start_date, end_date


@data.get('/routes')
def routes_data():
    '''Get data for routes page.'''
    start_date, end_date = get_dates()
    query_results = get_query_results(
        POPULAR_ROUTES_QUERY, start_date, end_date)

    results: ResultsDict = {'labels': [], 'datasets': []}

    results['labels'] = query_results['route'].to_list()
    results['datasets'] = [
        {'label': 'Validāciju skaits', 'data': query_results['count'].to_list()}]

    return jsonify(results)


@data.get('/times')
def times_data():
    '''Get data for times page.'''
    start_date, end_date = get_dates()
    query_results = get_query_results(
        VALIDATIONS_BY_HOUR_QUERY, start_date, end_date)

    query_results = query_results.groupby(
        'hour')['count'].sum().reset_index()
    query_results['route'] = 'Visi maršruti'

    results: ResultsDict = {'labels': [], 'datasets': []}

    results['labels'] = list(range(24))

    groups = query_results.groupby('route')
    routes = query_results['route'].unique().tolist()
    for route in sorted(routes):
        results['datasets'].append({'label': route, 'data': []})

    for dataset in results['datasets']:
        route_data = groups.get_group(dataset['label'])[['hour', 'count']]
        for hour in range(24):
            if hour in route_data['hour'].values:
                dataset['data'].append(
                    int(route_data.loc[route_data['hour'] == hour, 'count'].iloc[0]))
            else:
                dataset['data'].append(0)

    return jsonify(results)
