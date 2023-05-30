# For creating tables in db
from extensions import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(UserMixin, db.Model):
    id = db.Column( db.Integer, primary_key = True, autoincrement=True )
    full_name = db.Column(db.String(400), nullable = False)
    email = db.Column(db.String(400), nullable = False, unique=True)
    password = db.Column(db.String(255), nullable = False)

    def __init__ (self, full_name, email, password):
        self.full_name = full_name
        self.email = email
        self.password = password
    
    def save(self):
        db.session.add(self)
        db.session.commit()

class Contact(db.Model):
    id = db.Column( db.Integer, primary_key = True, autoincrement=True )
    full_name = db.Column(db.String(400), nullable = False)
    email = db.Column(db.String(400), nullable = False)
    subject = db.Column(db.String(400), nullable = False)
    message = db.Column(db.String(2000), nullable = False)

    def __init__ (self, full_name, email, subject, message):
        self.full_name = full_name
        self.email = email
        self.subject = subject
        self.message = message

    def save(self):
        db.session.add(self)
        db.session.commit()

class NewsTeller(db.Model):
    id = db.Column( db.Integer, primary_key = True, autoincrement=True )
    full_name = db.Column(db.String(400), nullable = False)
    email = db.Column(db.String(400), nullable = False)

    def __init__ (self, full_name, email):
        self.full_name = full_name
        self.email = email

    def save(self):
        db.session.add(self)
        db.session.commit()