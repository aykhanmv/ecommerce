from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo

import wtforms
import flask_wtf

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
    message = TextAreaField('message', validators=[DataRequired()])

class NewsTellerForm(FlaskForm):
    full_name = StringField('full_name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])

class ReviewForm(FlaskForm):
    content = TextAreaField('content', validators=[DataRequired()])

class SearchForm(FlaskForm):
    keyword = StringField('keyword', validators=[DataRequired()])
