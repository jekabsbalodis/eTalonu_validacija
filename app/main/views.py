'''
Main routes and view functions for the Flask application.
Includes database connection management and theme toggling
'''
from flask import render_template, redirect, session, request, url_for
from peewee import JOIN, fn
from app.models import sqlite_db, Validacijas, Marsruts
from . import main


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
    query = Validacijas.select(
        Marsruts.marsruts, fn.COUNT(Validacijas.id).alias('count')
    ).join(
        Marsruts, JOIN.LEFT_OUTER
    ).group_by(
        Marsruts.marsruts
    ).order_by(
        fn.COUNT(Validacijas.id).desc())

    results = [(result.marsruts_id.marsruts, result.count) for result in query]

    return render_template('routes.jinja', results=results)


@main.route('/times', methods=['GET'])
def times():
    '''Render the page with statistics of hours when public transportation is used the most'''
    query = (Validacijas
             .select(
                 Validacijas.laiks.hour.alias('hour'),
                 fn.COUNT(Validacijas.id).alias('count')
             )
             .join(Marsruts, JOIN.LEFT_OUTER).group_by(Validacijas.laiks.hour))

    results = [(result.hour, result.count) for result in query]

    return render_template('time.jinja', results=results)
