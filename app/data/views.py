'''
Data routes and view functions for the Flask app.
Includes routes that provide data for the corresponding main functions.
'''
from typing import TypedDict

import duckdb
from flask import current_app, jsonify

from app.data import data


class RouteDataDict(TypedDict):
    '''Define model for the data to hold validations for each route and hour.'''
    label: str
    data: list[int]


class ResultsDict(TypedDict):
    '''Define model for the dict containing all the results that will be passed to template for rendering.'''
    labels: list[int | str]
    datasets: list[RouteDataDict]


@data.get('/data/routes')
def routes_data():
    '''Get data for routes page.'''
    with duckdb.connect(current_app.config['DATABASE'], read_only=True) as con:
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

    results: ResultsDict = {'labels': [], 'datasets': []}

    for route, count in query_results:
        results['labels'].append(route)

    results['datasets'] = [{'label': 'Validāciju skaits mēnesī', 'data': [
        count for route, count in query_results]}]

    return jsonify(results)


@data.route('/data/times', methods=['GET', 'POST'])
def times_data():
    '''Get data for times page.'''
    with duckdb.connect(current_app.config['DATABASE'], read_only=True) as con:
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
        query_results = con.sql(query.format(*last_month)).fetchall()

    results: ResultsDict = {'labels': [], 'datasets': []}
    results["labels"] = list(range(24))

    for route, hour, count in query_results:
        # Check if route is already in the results dict
        if route not in [dataset["label"] for dataset in results["datasets"]]:
            results["datasets"].append(
                {"label": route, "data": [0] * 24})  # Initialize with 24 zeros

        # Find the dataset for the current route
        dataset = [dataset for dataset in results["datasets"]
                   if dataset["label"] == route][0]

        # Add the validation to the dataset's data list at the corresponding hour index
        dataset["data"][hour] = count

    results['datasets'] = sorted(
        results['datasets'], key=lambda dataset: dataset['label'])

    aggregated_data: RouteDataDict = {
        'label': 'Visi maršruti', 'data': [0] * 24}
    for route, hour, count in query_results:
        aggregated_data['data'][hour] += count
    results['datasets'].append(aggregated_data)

    results["labels"].sort()

    return jsonify(results)
