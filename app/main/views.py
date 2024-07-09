'''View functions for start page'''
# from flask import render_template
# from app import db_wrapper
from . import main


@main.route('/', methods=['GET'])
def index():
    '''View function for start page'''
    # query = db.session.execute(text('''SELECT marsruts, COUNT(*) AS count
    #                                         FROM validacijas
    #                                         GROUP BY marsruts
    #                                         ORDER BY count DESC
    #                                         LIMIT 10;'''))
    # results = query.all()
    # return render_template('index.html.jinja', results=results)
    return 'hello world'
