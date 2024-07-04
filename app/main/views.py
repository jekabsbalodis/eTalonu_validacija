'''View functions for start page'''
from flask import render_template
from . import main
from ..models import Validacijas


@main.route('/', methods=['GET'])
def index():
    '''View function for start page'''
    validacijas = Validacijas.query.filter_by(talona_id = 3673304).all()
    for validacija in validacijas:
        print(validacija.transp_veids)
    return render_template('index.html.jinja', validacijas=validacijas)
