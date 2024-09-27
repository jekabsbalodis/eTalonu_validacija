'''
Main routes and view functions for the Flask application.
Includes database connection management and theme toggling
'''
from flask import jsonify, render_template, redirect, session, request, url_for
from peewee import JOIN, fn
from app.models import sqlite_db, Validacijas, Marsruts
from . import main
import duckdb

@main.before_request
def _db_connect():
    sqlite_db.connect(reuse_if_open=True)


@main.teardown_request
def _db_close(exc):
    if not sqlite_db.is_closed():
        sqlite_db.close()


@main.get("/toggle-theme")
def toggle_theme():
    '''Toggle between light and dark themes'''
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"
    return redirect(request.args.get("current_page") or '/')


@main.route('/', methods=['GET'])
def index():
    '''Render the start page of the app'''
    return render_template('index.jinja')


@main.route('/routes', methods=['GET'])
def routes():
    '''Render the page with statistics of most used routes'''
    query = (Validacijas.
             select(
                 Marsruts.marsruts. alias('route'), fn.COUNT(Validacijas.id).alias('count')
             ).join(
                 Marsruts, JOIN.LEFT_OUTER
             ).group_by(
                 Marsruts.marsruts
             ).order_by(
                 fn.COUNT(Validacijas.id).desc()))

    results = list(query.tuples().iterator())

    return render_template('routes.jinja', results=results)


@main.route('/times', methods=['GET'])
def times():
    '''Render the page with statistics of hours when public transportation is used the most'''
    data_url = url_for('main.times_data')
    return render_template('time.jinja', data_url=data_url)


@main.get("/times_data")
def times_data():
    '''Get data for times page'''
    results = []

    # Connect to DuckDB database
    con = duckdb.connect("file.db")

    # SQL query to get the number of validations per hour per route
    query = """
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
    """

    # Execute the query
    query_results = con.execute(query).fetchall()

    # Process the query results
    for route, hour, count in query_results:
        # Find existing route in results
        existing_route = next((r for r in results if r["route"] == route), None)
        
        if existing_route:
            # If route exists, update its validations for the specific hour
            existing_route["validations"][int(hour)] = count
        else:
            # If route doesn't exist, create a new route entry with validations
            route_dict = {
                "route": route,
                "validations": {int(hour): count}
            }
            results.append(route_dict)

    # Ensure every route has validation counts for all 24 hours (default to 0)
    for route_dict in results:
        for hour in range(24):
            if hour not in route_dict["validations"]:
                route_dict["validations"][hour] = 0

    # Return the results as JSON
    return jsonify(results)
