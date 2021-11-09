from werkzeug.utils import html
import wtforms as f
import wtforms.fields.html5 as html5
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    email = html5.EmailField('Email address', validators=[DataRequired(), Email()]) #f.StringField('email', validators=[DataRequired(), Email()])
    firstname = f.StringField('First name', validators=[DataRequired()])
    lastname = f.StringField('Last name', validators=[DataRequired()])
    password = f.PasswordField('Password', validators=[DataRequired()])
    date_of_birth = html5.DateField('Date of birth') #f.DateField('date_of_birth', format='%d/%m/%Y')
    display = ['email', 'firstname', 'lastname', 'password', 'date_of_birth']
