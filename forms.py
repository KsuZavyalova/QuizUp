# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired

class OptionForm(FlaskForm):
    text = StringField('Option', validators=[DataRequired()])

class PollForm(FlaskForm):
    question = StringField('Question', validators=[DataRequired()])
    options = FieldList(StringField('Option', validators=[DataRequired()]), min_entries=2, max_entries=5)
    submit = SubmitField('Create Poll')