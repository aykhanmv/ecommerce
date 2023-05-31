# For creating tables in db
from extensions import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(UserMixin, db.Model):
    __tablename__ = "user"
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
    __tablename__ = "contact"
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
    __tablename__ = "newsteller"
    id = db.Column( db.Integer, primary_key = True, autoincrement=True )
    full_name = db.Column(db.String(400), nullable = False)
    email = db.Column(db.String(400), nullable = False)

    def __init__ (self, full_name, email):
        self.full_name = full_name
        self.email = email

    def save(self):
        db.session.add(self)
        db.session.commit()


class Product(db.Model):
    __tablename__ = "product"
    id = db.Column( db.Integer, primary_key = True, autoincrement=True )
    title = db.Column(db.String(255), nullable = False)
    versions = db.relationship('ProductVersion', backref = db.backref('product'))
    categories = db.relationship('ProductCategoryRel', backref = db.backref('product'))

    def __init__ (self, title):
        self.title = title

    def save(self):
        db.session.add(self)
        db.session.commit()

class ProductVersion(db.Model):
    __tablename__ = "productversion"
    id = db.Column( db.Integer, primary_key = True, autoincrement=True )
    description = db.Column(db.String(2000), nullable = False)
    price = db.Column(db.Numeric(precision=10, scale=2, asdecimal=False, decimal_return_scale=None), nullable = False)
    main_image = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable = False)
    sizes = db.relationship('ProductVersionSize', backref = db.backref('productversion'))
    images = db.relationship('ProductVersionImages', backref = db.backref('productversion'))

    def __init__ (self, description, price, main_image, product_id):
        self.description = description
        self.price = price
        self.main_image = main_image
        self.product_id = product_id

    def save(self):
        db.session.add(self)
        db.session.commit()

class ProductVersionImages(db.Model):
    __tablename__ = "productversionimages"
    id = db.Column( db.Integer, primary_key = True, autoincrement=True )
    images = db.Column(db.String(255), nullable=False)
    product_version_id = db.Column(db.Integer, db.ForeignKey('productversion.id'), nullable = False)

    def __init__ (self, images, product_version_id):
        self.images = images
        self.product_version_id = product_version_id

    def save(self):
        db.session.add(self)
        db.session.commit()


class ProductVersionSize(db.Model):
    __tablename__ = "productversionsize"
    id = db.Column( db.Integer, primary_key = True, autoincrement=True )
    name = db.Column(db.String(10), nullable = False)
    product_version_id = db.Column(db.Integer, db.ForeignKey('productversion.id'), nullable = False)

    def __init__ (self, name, product_version_id):
        self.name = name
        self.product_version_id = product_version_id

    def save(self):
        db.session.add(self)
        db.session.commit()

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column( db.Integer, primary_key = True, autoincrement=True )
    name = db.Column(db.String(250), nullable = False)
    products = db.relationship('ProductCategoryRel', backref = db.backref('category'))

    def __init__ (self, name):
        self.name = name

    def save(self):
        db.session.add(self)
        db.session.commit()

class ProductCategoryRel(db.Model):
    __tablename__ = "productcategoryrel"
    id = db.Column( db.Integer, primary_key = True, autoincrement=True )
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable = False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable = False)

    def __init__ (self, product_id, category_id):
        self.product_id = product_id
        self.category_id = category_id

    def save(self):
        db.session.add(self)
        db.session.commit()