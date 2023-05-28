from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email 

class Register(FlaskForm):
    full_name = StringField('full_name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    password_confirmation = PasswordField('password_confirmation', validators=[DataRequired()])
