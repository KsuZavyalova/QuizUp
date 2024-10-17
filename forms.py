# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FieldList
from wtforms.validators import DataRequired, Length, EqualTo

class OptionForm(FlaskForm):
    text = StringField('Вариант ответа', validators=[DataRequired()])

class PollForm(FlaskForm):
    question = StringField('Вопрос', validators=[DataRequired(), Length(min=1, max=200)])
    options = FieldList(StringField('Вариант ответа', validators=[DataRequired(), Length(min=1, max=100)]), min_entries=2, max_entries=5)
    submit = SubmitField('Создать Опрос')

class RegisterForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password', message='Пароли должны совпадать')])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')
