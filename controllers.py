from app import app
from flask import render_template, request, redirect, url_for
from email_validator import validate_email, EmailNotValidError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError

from forms import RegisterForm, LoginForm, ContactForm, NewsTellerForm
from models import User, Contact, NewsTeller
from response_contet import responses

@app.route("/", methods = ['GET', 'POST'])
def home():
    newstellerForm = NewsTellerForm()
    response = {
        'has_response': -1,
        'form' : '',
        'response_content': []
    }
    if request.method == 'POST' and 'newsteller' in request.form:
            newstellerForm = NewsTellerForm(request.form)
            if newstellerForm.validate_on_submit():
                subscriber = NewsTeller (
                    full_name = newstellerForm.full_name.data,
                    email = newstellerForm.email.data,
                )
                subscriber.save()
                response['has_response'] = 0
                response['form'] = 'newsteller'
                response['response_content'].append(responses['subscribed'])
                return render_template('home.html', newstellerForm = newstellerForm, response = response)
            else:
                if not newstellerForm.full_name.data:
                    response['has_response'] = 1
                    response['form'] = 'newsteller'
                    response['response_content'].append(responses['fname'])
                if not newstellerForm.email.data:
                    response['has_response'] = 1
                    response['form'] = 'newsteller'
                    response['response_content'].append(responses['email'])
                if newstellerForm.email.data:
                    try:
                        validate_email(newstellerForm.email.data)
                    except EmailNotValidError as e:
                        response['has_response'] = 1
                        response['form'] = 'newsteller'
                        response['response_content'].append(responses['invalid_email'])
                    
                return render_template('home.html', newstellerForm = newstellerForm, response = response)

    return render_template('home.html', newstellerForm = newstellerForm, response = response)

@app.route("/register/",  methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home.html"))
    
    registerForm = RegisterForm()
    newstellerForm = NewsTellerForm()

    response = {
        'has_response': -1,
        'form' : '',
        'response_content': []
    }

    if request.method == 'POST':
        if 'register' in request.form:

            registerForm = RegisterForm(request.form)
            if registerForm.validate_on_submit():
                try: 
                    user = User(
                        full_name = registerForm.full_name.data,
                        email = registerForm.email.data,
                        password = generate_password_hash(registerForm.password.data)
                    )
                    user.save()
                    response['has_response'] = 0
                    response['form'] = 'register'
                    return render_template('register.html', registerForm = registerForm, newstellerForm = newstellerForm, response = response)
                except IntegrityError as err:
                    response['has_response'] = 1
                    response['form'] = 'register'
                    response['response_content'].append(responses['non_unique_email'])
                    return render_template('register.html', registerForm = registerForm, newstellerForm = newstellerForm,  response = response)


            else:
                if not registerForm.full_name.data:
                    response['has_response'] = 1
                    response['form'] = 'register'
                    response['response_content'].append(responses['fname'])
                if not registerForm.email.data:
                    response['has_response'] = 1
                    response['form'] = 'register'
                    response['response_content'].append(responses['email'])
                if not registerForm.password.data:
                    response['has_response'] = 1
                    response['form'] = 'register'
                    response['response_content'].append(responses['passwd'])         
                if not registerForm.password_confirmation.data:
                    response['has_response'] = 1
                    response['form'] = 'register'
                    response['response_content'].append(responses['passwd_conf']) 
                if registerForm.password.data != registerForm.password_confirmation.data:
                    response['has_response'] = 1
                    response['form'] = 'register'
                    response['response_content'].append(responses['unmatching_passwd'])
                if registerForm.email.data:
                    try:
                        validate_email(registerForm.email.data)
                    except EmailNotValidError as e:
                        response['has_response'] = 1
                        response['form'] = 'register'
                        response['response_content'].append(responses['invalid_email'])
                    
                return render_template('register.html', registerForm = registerForm, newstellerForm = newstellerForm,  response = response)
    
        elif 'newsteller' in request.form:
            newstellerForm = NewsTellerForm(request.form)
            if newstellerForm.validate_on_submit():
                subscriber = NewsTeller (
                    full_name = newstellerForm.full_name.data,
                    email = newstellerForm.email.data,
                )
                subscriber.save()
                response['has_response'] = 0
                response['form'] = 'newsteller'
                response['response_content'].append(responses['subscribed'])
                return render_template('register.html', registerForm = registerForm, newstellerForm = newstellerForm, response = response)
            else:
                if not newstellerForm.full_name.data:
                    response['has_response'] = 1
                    response['form'] = 'newsteller'
                    response['response_content'].append(responses['fname'])
                if not newstellerForm.email.data:
                    response['has_response'] = 1
                    response['form'] = 'newsteller'
                    response['response_content'].append(responses['email'])
                if newstellerForm.email.data:
                    try:
                        validate_email(newstellerForm.email.data)
                    except EmailNotValidError as e:
                        response['has_response'] = 1
                        response['form'] = 'newsteller'
                        response['response_content'].append(responses['invalid_email'])
                    
                return render_template('register.html', registerForm = registerForm, newstellerForm = newstellerForm, response = response)

    return render_template('register.html', registerForm = registerForm, newstellerForm = newstellerForm,  response = response)

@app.route("/login/", methods = ['GET', 'POST'])
def login():
    loginForm = LoginForm()
    newstellerForm = NewsTellerForm()

    response = {
        'has_response': -1,
        'form' : '',
        'response_content': []
    }

    if request.method == 'POST':
        if 'login' in request.form:
            user = User.query.filter_by( email = loginForm.email.data ).first()
            if user and check_password_hash(user.password, loginForm.password.data):
                login_user(user)
                return render_template('home.html', newstellerForm = newstellerForm, response = response)
            else:
                response['has_response'] = 1
                response['form'] = 'login'
                response['response_content'].append(responses['invalid_user'])
                return render_template('login.html', loginForm = loginForm, newstellerForm = newstellerForm, response = response)
        
        elif 'newsteller' in request.form:
            newstellerForm = NewsTellerForm(request.form)
            if newstellerForm.validate_on_submit():
                subscriber = NewsTeller (
                    full_name = newstellerForm.full_name.data,
                    email = newstellerForm.email.data,
                )
                subscriber.save()
                response['has_response'] = 0
                response['form'] = 'newsteller'
                response['response_content'].append(responses['subscribed'])
                return render_template('login.html', loginForm = loginForm, newstellerForm = newstellerForm, response = response)
            else:
                if not newstellerForm.full_name.data:
                    response['has_response'] = 1
                    response['form'] = 'newsteller'
                    response['response_content'].append(responses['fname'])
                if not newstellerForm.email.data:
                    response['has_response'] = 1
                    response['form'] = 'newsteller'
                    response['response_content'].append(responses['email'])
                if newstellerForm.email.data:
                    try:
                        validate_email(newstellerForm.email.data)
                    except EmailNotValidError as e:
                        response['has_response'] = 1
                        response['form'] = 'newsteller'
                        response['response_content'].append(responses['invalid_email'])
                    
                return render_template('login.html', loginForm = loginForm, newstellerForm = newstellerForm, response = response)

    return render_template('login.html', loginForm = loginForm, newstellerForm = newstellerForm, response = response)

@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/favorites/")
def favorites():
    return render_template('favorites.html')

@app.route("/contact/", methods = ['GET', 'POST'])
def contact():
    contactForm = ContactForm()
    newstellerForm = NewsTellerForm()

    response = {
        'has_response': -1,
        'form' : '',
        'response_content': []
    }

    if request.method == 'POST':
        if 'contact' in request.form:
            contactForm = ContactForm(request.form)

            if contactForm.validate_on_submit():
                contact = Contact (
                    full_name = contactForm.full_name.data,
                    email = contactForm.email.data,
                    subject = contactForm.subject.data,
                    message = contactForm.message.data
                )
                contact.save()
                response['has_response'] = 0
                response['form'] = 'contact'
                response['response_content'].append(responses['sent_message'])
                return render_template('contact.html', contactForm = contactForm, newstellerForm = newstellerForm, response = response)

            else:
                if not contactForm.full_name.data:
                    response['has_response'] = 1
                    response['form'] = 'contact'
                    response['response_content'].append(responses['fname'])
                if not contactForm.email.data:
                    response['has_response'] = 1
                    response['form'] = 'contact'
                    response['response_content'].append(responses['email'])
                if not contactForm.subject.data:
                    response['has_response'] = 1
                    response['form'] = 'contact'
                    response['response_content'].append(responses['subject'])         
                if not contactForm.message.data:
                    response['has_response'] = 1
                    response['form'] = 'contact'
                    response['response_content'].append(responses['message']) 
                if contactForm.email.data:
                    try:
                        validate_email(contactForm.email.data)
                    except EmailNotValidError as e:
                        response['has_response'] = 1
                        response['form'] = 'contact'
                        response['response_content'].append(responses['invalid_email'])
                return render_template('contact.html', contactForm = contactForm, newstellerForm = newstellerForm, response = response)
            
        elif 'newsteller' in request.form:
            newstellerForm = NewsTellerForm(request.form)
            if newstellerForm.validate_on_submit():
                subscriber = NewsTeller (
                    full_name = newstellerForm.full_name.data,
                    email = newstellerForm.email.data,
                )
                subscriber.save()
                response['has_response'] = 0
                response['form'] = 'newsteller'
                response['response_content'].append(responses['subscribed'])
                return render_template('contact.html', contactForm = contactForm, newstellerForm = newstellerForm, response = response)
            else:
                if not newstellerForm.full_name.data:
                    response['has_response'] = 1
                    response['form'] = 'newsteller'
                    response['response_content'].append(responses['fname'])
                if not newstellerForm.email.data:
                    response['has_response'] = 1
                    response['form'] = 'newsteller'
                    response['response_content'].append(responses['email'])
                if newstellerForm.email.data:
                    try:
                        validate_email(newstellerForm.email.data)
                    except EmailNotValidError as e:
                        response['has_response'] = 1
                        response['form'] = 'newsteller'
                        response['response_content'].append(responses['invalid_email'])
                    
                return render_template('contact.html', contactForm = contactForm, newstellerForm = newstellerForm, response = response)

    return render_template('contact.html', contactForm = contactForm, newstellerForm = newstellerForm, response = response)

@app.route("/detail/", methods = ['GET', 'POST'])
def detail():
    newstellerForm = NewsTellerForm()
    response = {
        'has_response': -1,
        'form' : '',
        'response_content': []
    }
    if request.method == 'POST' and 'newsteller' in request.form:
            newstellerForm = NewsTellerForm(request.form)
            if newstellerForm.validate_on_submit():
                subscriber = NewsTeller (
                    full_name = newstellerForm.full_name.data,
                    email = newstellerForm.email.data,
                )
                subscriber.save()
                response['has_response'] = 0
                response['form'] = 'newsteller'
                response['response_content'].append(responses['subscribed'])
                return render_template('detail.html', newstellerForm = newstellerForm, response = response)
            else:
                if not newstellerForm.full_name.data:
                    response['has_response'] = 1
                    response['form'] = 'newsteller'
                    response['response_content'].append(responses['fname'])
                if not newstellerForm.email.data:
                    response['has_response'] = 1
                    response['form'] = 'newsteller'
                    response['response_content'].append(responses['email'])
                if newstellerForm.email.data:
                    try:
                        validate_email(newstellerForm.email.data)
                    except EmailNotValidError as e:
                        response['has_response'] = 1
                        response['form'] = 'newsteller'
                        response['response_content'].append(responses['invalid_email'])
                    
                return render_template('detail.html', newstellerForm = newstellerForm, response = response)

    return render_template('detail.html', newstellerForm = newstellerForm, response = response)