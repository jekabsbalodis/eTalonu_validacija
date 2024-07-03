'''View functions for start page'''
from flask import jsonify
from . import main


@main.route('/', methods=['GET'])
def index():
    '''View function for start page'''
    return jsonify('hello world')
