from app import app
from flask import render_template, request, redirect, url_for
from forms import RegisterForm, LoginForm
from models import User
from email_validator import validate_email, EmailNotValidError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/register/",  methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    error_message = {
        'has_error': -1,
        'error_content': []
    }
    # If method is 'POST' the variable "form" will take data filled by the user via "Register" form.
    if request.method == 'POST':
        form = RegisterForm(request.form)

        # To check if the form is filled properly based on requisitions
        if form.validate_on_submit():
            user = User(
                full_name = form.full_name.data,
                email = form.email.data,
                password = generate_password_hash(form.password.data)
            )
            user.save()
            error_message['has_error'] = 0
            return render_template('register.html', form = form, error_message = error_message)

        else:
            if not form.full_name.data:
                error_message['has_error'] = 1
                error_message['error_content'].append('You have not filled your Full Name')
            if not form.email.data:
                error_message['has_error'] = 1
                error_message['error_content'].append('You have not filled your Email')
            if not form.password.data:
                error_message['has_error'] = 1
                error_message['error_content'].append('You have not filled your Password')         
            if not form.password_confirmation.data:
                error_message['has_error'] = 1
                error_message['error_content'].append('You have not filled your Password Confirmation') 

            if form.password.data != form.password_confirmation.data:
                error_message['has_error'] = 1
                error_message['error_content'].append('Passwords do not match')
            if form.email.data:
                try:
                    validate_email(form.email.data)
                except EmailNotValidError as e:
                    error_message['has_error'] = 1
                    error_message['error_content'].append('The email you entered is not valid')
                
            return render_template('register.html', form = form, error_message = error_message)
            
    return render_template('register.html', form = form, error_message = error_message)

@app.route("/login/", methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    error_message = {
        'has_error': -1,
        'error_content': []
    }
    if request.method == 'POST':
        user = User.query.filter_by( email = form.email.data ).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return render_template('home.html', form = form)
        else:
            error_message['has_error'] = 1
            error_message['error_content'].append('Invalid username or password. Please try again.')

            return render_template('login.html', form = form, error_message = error_message)

    return render_template('login.html', form = form, error_message = error_message)

@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/favorites/")
def favorites():
    return render_template('favorites.html')

@app.route("/contact/")
def contact():
    return render_template('contact.html')
