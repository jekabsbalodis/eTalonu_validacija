'''View functions for start page'''
from flask import render_template
from . import main
from app.models import sqlite_db, Validacijas, Marsruts
from peewee import JOIN, fn


@main.before_request
def _db_connect():
    sqlite_db.connect(reuse_if_open=True)


@main.teardown_request
def _db_close(exc):
    if not sqlite_db.is_closed():
        sqlite_db.close()


@main.route('/', methods=['GET'])
def index():
    '''View function for start page'''
    query = Validacijas.select(Marsruts.marsruts, fn.COUNT(Validacijas.id).alias('count')).join(
        Marsruts, JOIN.LEFT_OUTER).group_by(Marsruts.marsruts).order_by(fn.COUNT(Validacijas.id).asc()).limit(10)
    
    results = [(result.marsruts_id.marsruts, result.count) for result in query]

    # for query_dict in query:
    #     print(query_dict.marsruts_id.marsruts)
    #     print(query_dict.count)
    # results = query.all()
    # query = db.session.execute(text('''SELECT marsruts, COUNT(*) AS count
    #                                         FROM validacijas
    #                                         GROUP BY marsruts
    #                                         ORDER BY count DESC
    #                                         LIMIT 10;'''))
    # results = query.all()
    print(type(query))
    return render_template('index.html.jinja', results=results)