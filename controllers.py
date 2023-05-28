from app import app
from flask import render_template

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/register/")
def register():
    return render_template('register.html')

@app.route("/login/")
def login():
    return render_template('login.html')

@app.route("/favorites/")
def favorites():
    return render_template('favorites.html')

@app.route("/contact/")
def contact():
    return render_template('contact.html')
