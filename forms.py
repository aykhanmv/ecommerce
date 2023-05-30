from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo

class RegisterForm(FlaskForm):
    full_name = StringField('full_name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    password_confirmation = PasswordField('password_confirmation', validators=[DataRequired(), EqualTo('password')])

class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])

class ContactForm(FlaskForm):
    full_name = StringField('full_name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    subject = StringField('subject', validators=[DataRequired()])
    message = StringField('message', validators=[DataRequired()])

class NewsTellerForm(FlaskForm):
    full_name = StringField('full_name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
