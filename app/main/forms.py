'''
Forms to select arguments to pass to view functions
'''

import duckdb
from flask import current_app
from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField, ValidationError
from wtforms.validators import DataRequired


def date_range_check(self, field):
    '''Validator to check if selected date is in valid date range'''

    with duckdb.connect(current_app.config['DATABASE'], read_only=True) as con:
        date_range = con.sql('''
                    SELECT
                        date_trunc('day', MIN(Laiks)) AS min_time,
                        date_trunc('day', MAX(Laiks)) AS max_time
                    FROM
                        validacijas
                    ''').fetchone()
    if date_range:
        out_of_range_error = f'Datubāzē pieejami ieraksti no {
            date_range[0]} līdz {date_range[1]}.'
        if field.data < date_range[0] or field.data > date_range[1]:
            raise ValidationError(out_of_range_error)


class DateSelectForm(FlaskForm):
    '''Form to select the date and year for data display.'''

    start_date = DateField('Sākuma datums', validators=[
                           DataRequired(message='Lūdzu norādi datumu.'), date_range_check])
    end_date = DateField('Beigu datums', validators=[
                         DataRequired(message='Lūdzu norādi datumu.'), date_range_check])
    submit = SubmitField('Atlasīt')

    def validate_end_date(self, field):
        '''Validator to check if end_date is after start_date'''

        if field.data < self.start_date.data:
            raise ValidationError(
                'Beigu datums nevar būt pirms sākuma datuma.')
