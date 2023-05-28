from app import app
from flask import render_template, request
from forms import Register
from models import User
from email_validator import validate_email, EmailNotValidError

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/register/",  methods = ['GET', 'POST'])
def register():
    form = Register()
    error_message = {
        'has_error': 0,
        'error_content': []
    }
    # If method is 'POST' the variable "form" will take data filled by the user via "Register" form.
    if request.method == 'POST':
        form = Register(request.form)

        # To check if the form is filled properly based on requisitions
        if form.validate_on_submit():

            if form.password.data != form.password_confirmation.data:
                error_message['has_error'] = 1
                error_message['error_content'].append('Passwords do not match')
                return render_template('register.html', form = form, error_message = error_message)

            else:    
                user = User(
                    full_name = form.full_name.data,
                    email = form.email.data,
                    password = form.password.data
                )
                user.save()
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

            if form.email.data:
                try:
                    validate_email(form.email.data)
                except EmailNotValidError as e:
                    error_message['has_error'] = 1
                    error_message['error_content'].append('The email you entered is not valid')
                
            return render_template('register.html', form = form, error_message = error_message)
            
    return render_template('register.html', form = form, error_message = error_message)

@app.route("/login/")
def login():
    return render_template('login.html')

@app.route("/favorites/")
def favorites():
    return render_template('favorites.html')

@app.route("/contact/")
def contact():
    return render_template('contact.html')
