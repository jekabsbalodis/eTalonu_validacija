'''
Ajax routes and view functions for the Flask app.
Includes routes to return partial html for the corresponding main functions
'''
from flask import Response, make_response, render_template, url_for
from app.ajax import ajax
from app.main.forms import DateSelectForm
from app.main.views import get_time_range


def ajax_date_form(data_route: str, ajax_route: str) -> Response:
    '''
    Function to return errors if server side form
    validation fails or to return url for the modified data.
    '''
    form = DateSelectForm()
    time_range = get_time_range()
    template = 'partials/date_select_form.jinja'
    ajax_url = url_for(ajax_route)

    if form.validate_on_submit():
        data_url = url_for(
            data_route, start_date=form.start_date.data, end_date=form.end_date.data)
        post_request_successful = True
        status_code = 200
    else:
        data_url = url_for(data_route)
        post_request_successful = False
        status_code = 422

    response = make_response(render_template(
        template,
        form=form,
        urls=(data_url, ajax_url),
        time_range=time_range,
        post_request_successful=post_request_successful), status_code)
    return response


@ajax.post('/routes')
def routes_ajax():
    '''Handle date form in routes view.'''
    res = ajax_date_form('data.routes_data', 'ajax.routes_ajax')
    return res


@ajax.post('/times')
def times_ajax():
    '''Handle date form in times view.'''
    res = ajax_date_form('data.times_data', 'ajax.times_ajax')
    return res
