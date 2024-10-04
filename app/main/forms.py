'''
Forms to select arguments to pass to view functions
'''

from flask_wtf import FlaskForm
from wtforms import SubmitField, DateField, ValidationError
from wtforms.validators import DataRequired


class MonthSelectForm(FlaskForm):
    '''Form to select the date and year for data display.'''
    start_date = DateField('Sākuma datums', validators=[DataRequired()])
    end_date = DateField('Beigu datums', validators=[DataRequired()])
    submit = SubmitField('Atlasīt')

    def validate_end_date(self, field):
        '''Validator to check if end_date is after start_date'''
        if field.data < self.start_date.data:
            raise ValidationError(
                'Beigu datums nevar būt pirms sākuma datuma.')
