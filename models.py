# For creating tables in db

from extensions import db

class User(db.Model):
    id = db.Column( db.Integer, primary_key = True, autoincrement=True )
    full_name = db.Column(db.String(300), nullable = False)
    email = db.Column(db.String(400), nullable = False)
    password = db.Column(db.String(200), nullable = False)

    def __init__ (self, full_name, email, password):
        self.full_name = full_name
        self.email = email
        self.password = password
    
    def save(self):
        db.session.add(self)
        db.session.commit()