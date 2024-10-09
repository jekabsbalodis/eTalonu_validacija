'''
Validation routes and view functions for the Flask application.
'''
from time import strptime
from flask import render_template, request, url_for

from app.main.forms import TimeSelectForm
from app.validation import validation


@validation.route('/validate/date', methods=['POST'])
def validate_date():
    '''Validate the date user has entered.'''
    form = TimeSelectForm()
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    if not (start_date):
        return_class = 'is-invalid'
        error_message = 'Ievadi datumu'
        validation_url = url_for('validation.validate_date')
        return render_template('parts/validate_date.jinja', form=form, return_class=return_class, error_message=error_message, validation_url=validation_url)
    start_date = strptime(start_date, '%Y-%m-%d')
    end_date = strptime(end_date, '%Y-%m-%d')
    if start_date > end_date:
        print('sākums lielāks nekā beigas')
        return_value = '''
                {{ form.end_date.label(class_='form-label') }}
                {{ form.end_date(class_='form-control is-invalid', **{'hx-post': url_for("validation.validate_date")}) }}
            '''
    else:
        print('beigas lielākas nekā sākums')
        return_value = '''
                {{ form.end_date.label(class_='form-label') }}
                {{ form.end_date(class_='form-control is-valid', **{'hx-post': url_for("validation.validate_date")}) }}
            '''
    return render_template_string(return_value, form=form)
