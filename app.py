from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_wtf.file import FileField, FileAllowed
from werkzeug.datastructures import FileStorage
import os
import uuid

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+mysqlconnector://admin:admin@127.0.0.1:3306/ecommerce'
app.config["SECRET_KEY"] = 'project'
app.config['UPLOAD_FOLDER'] = 'static/media'

from controllers import *
from models import *
from extensions import *

if __name__ == '__main__':
    app.init_app(db)
    app.init_app(migrate)

from models import *

admin = Admin(app)

def generate_unique_filename(filename):
    ext = os.path.splitext(filename)[1]
    unique_filename = str(uuid.uuid4()) + ext
    return unique_filename

class UserView(ModelView):
    column_display_pk = True
    form_columns = ['full_name', 'email', 'password', 'is_superuser']
    column_list = ['id', 'full_name', 'email', 'password', 'is_superuser', 'created_at']
    column_searchable_list = ['full_name', 'email']
    column_filters = ['is_superuser']

class ContactView(ModelView):
    column_display_pk = True
    form_columns = ['full_name', 'email','subject', 'message']
    column_list = ['id', 'full_name', 'email', 'subject', 'message', 'created_at']
    column_searchable_list = ['full_name', 'email', 'subject', 'message']
    column_filters = ['full_name', 'email']

class NewsletterView(ModelView):
    column_display_pk = True
    form_columns = ['full_name', 'email']
    column_list = ['id', 'full_name', 'email', 'created_at']
    column_searchable_list = ['full_name', 'email']
    column_filters = []

class ProductView(ModelView):
    form_extra_fields = {
        'cover_image': FileField('Cover Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'webp'], 'Images only!')])
    }
    def on_model_change(self, form, model, is_created):
        file = form.cover_image.data
        if isinstance(file, FileStorage):  # Check if it's a FileStorage object
            filename = secure_filename(file.filename)
            unique_filename = generate_unique_filename(filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))
            model.cover_image = unique_filename
        elif model.id is not None:  # Check if it's an existing model (not a newly created one)
            # Retain the previous cover image if no new file is provided
            previous_model = self.session.query(self.model).get(model.id)
            model.cover_image = previous_model.cover_image
            
    column_display_pk = True
    form_columns = ['name', 'price', 'description', 'cover_image']
    column_list = ['id', 'name', 'price', 'description', 'cover_image']
    column_searchable_list = [ 'name', 'description']
    column_filters = []
    
class CategoryView(ModelView):
    column_display_pk = True    
    form_columns = ['name', 'parent_id']
    column_list = [ 'id', 'name', 'parent_id', 'parent_name']
    def _parent_name_formatter(view, context, model, name):
        return Category.query.filter_by(id = model.parent_id).first().name if model.parent_id else None
    column_formatters = {
            'parent_name': _parent_name_formatter
        }
    column_searchable_list = [ 'name']
    column_filters = []

class CategoryProductRelView(ModelView):
    column_display_pk = True
    form_columns = ['product_id', 'category_id']
    column_list = ['id', 'product_id', 'product_name', 'category_id', 'category_name']

    def _product_name_formatter(view, context, model, name):
        return Product.query.filter_by(id=model.product_id).first().name if model.product_id else None
    def _category_name_formatter(view, context, model, name):
        return Category.query.filter_by(id=model.category_id).first().name if model.category_id else None
    column_formatters = {
        'product_name': _product_name_formatter,
        'category_name': _category_name_formatter
    }
    column_searchable_list = []
    column_filters = []

class ImageView(ModelView):
    column_display_pk = True
    form_columns = ['image', 'product_id']
    column_searchable_list = [ 'product_id']
    column_filters = ['product_id']

class ReviewView(ModelView):
    column_display_pk = True
    form_columns = ['content', 'user_id', 'product_id']
    column_list = ['id', 'content', 'user_id', 'user_name', 'product_id','product_name', 'created_at']

    def _user_name_formatter(view, context, model, name):
        return User.query.filter_by(id=model.user_id).first().full_name if model.user_id else None
    def _product_name_formatter(view, context, model, name):
        return Product.query.filter_by(id=model.product_id).first().name if model.product_id else None
    column_formatters = {
        'user_name': _user_name_formatter,
        'product_name': _product_name_formatter
    }
    column_searchable_list = ['content', 'user_id', 'product_id']
    column_filters = ['product_id', 'user_id']

class FavoritesView(ModelView):
    column_display_pk = True
    form_columns = ['user_id', 'product_id']
    column_list = ['id', 'user_id', 'user_name', 'product_id', 'product_name', 'created_at']

    def _user_name_formatter(view, context, model, name):
        return User.query.filter_by(id=model.user_id).first().full_name if model.user_id else None
    def _product_name_formatter(view, context, model, name):
        return Product.query.filter_by(id=model.product_id).first().name if model.product_id else None
    column_formatters = {
        'user_name': _user_name_formatter,
        'product_name': _product_name_formatter
    }
    column_searchable_list = ['user_id', 'product_id']
    column_filters = ['user_id', 'product_id']
class DiscountsView(ModelView):
    column_display_pk = True
    form_columns = ['percent', 'product_id']
    column_list = ['id', 'percent', 'product_id', 'product_name', 'created_at']
    def _product_name_formatter(view, context, model, name):
        return Product.query.filter_by(id=model.product_id).first().name if model.product_id else None
    column_formatters = {
        'product_name': _product_name_formatter
    }
    column_searchable_list = ['percent', 'product_id']
    column_filters = ['product_id']

admin.add_view(UserView(User, db.session))
admin.add_view(ContactView(Contact, db.session))
admin.add_view(NewsletterView(Newsletter, db.session))
admin.add_view(ProductView(Product, db.session))
admin.add_view(CategoryView(Category, db.session))
admin.add_view(CategoryProductRelView(Categoryproductrel, db.session))
admin.add_view(ImageView(Image, db.session))
admin.add_view(ReviewView(Review, db.session))
admin.add_view(FavoritesView(Favorites, db.session))
admin.add_view(DiscountsView(Discounts, db.session))




