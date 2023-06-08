from app import app
from flask import render_template, request, redirect, url_for, flash
from email_validator import validate_email, EmailNotValidError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.exc import IntegrityError
from response_contet import responses

from forms import RegisterForm, LoginForm, ContactForm, NewsTellerForm, ReviewForm, SearchForm
from models import User, Contact, Newsletter, Product, Category, Categoryproductrel, Favorites, Review, Discounts
from extensions import db

# =============================================================== BEFORE REQUEST ===

auth_required_routes = ['/admin/', '/favorites/', '/add-favorite/<int:productid>', '/remove-favorite/<int:productid>']
privilage_required_routes = ['/admin/']

@app.before_request
def check_authentication():
    if request.path in auth_required_routes:
        if not current_user.is_authenticated:
            flash({'content' : ['You have to log in to visit that page!'], 'type' : 'danger', 'role' : 'base'})
            return redirect(url_for('login'))

@app.before_request
def check_privilage():
    if request.path in privilage_required_routes:
        if not current_user.is_superuser:
            flash({'content' : ['You dont have proper privilages to visit that page!'], 'type' : 'danger', 'role' : 'base'})
            return redirect(url_for('home'))

# =============================================================== CONTEXT PROCESSORS ===

@app.context_processor
def categories_global():
    all_categories = Category.query.all()
    return dict(all_categories = all_categories)

@app.context_processor
def newsteller_global():
    newstellerForm = NewsTellerForm()
    return dict(newstellerForm = newstellerForm)

@app.context_processor
def searchbar_global():
    searchForm = SearchForm()
    return dict(searchForm = searchForm)

@app.context_processor
def category_names_global():
    categories = Category.query.with_entities(Category.name).distinct().all()
    category_names = [category[0] for category in categories]
    return dict(category_names = category_names)

@app.context_processor
def numberof_favorites_global():
    if current_user.is_authenticated:
        numberof_favorites = len( Favorites.query.filter_by(user_id = current_user.id ).all() )
    else:
        numberof_favorites = 0
        
    return dict(numberof_favorites = numberof_favorites)

PRODUCTS_PER_PAGE = 9

@app.context_processor
def all_products_global():
    page = request.args.get('page', 1, type=int)
    all_products = Product.query.order_by(Product.id.desc()).paginate(page=page, per_page=PRODUCTS_PER_PAGE)

    product_ids = [product.id for product in all_products]
    discounts = Discounts.query.filter(Discounts.product_id.in_(product_ids)).all()
    discount_mapping = {}  
    for discount in discounts:
        discount_mapping[discount.product_id] = discount
        
    return dict(all_products=all_products, discount_mapping = discount_mapping)


# =============================================================== ROUTERS ===

PRODUCTS_PER_PAGE = 9
@app.route("/", methods = ['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'newsteller' in request.form:
            newstellerForm = NewsTellerForm(request.form)
            if newstellerForm.validate_on_submit():
                subscriber = Newsletter (
                    full_name = newstellerForm.full_name.data,
                    email = newstellerForm.email.data,
                )
                try:
                    subscriber.save()
                    flash({'content' : ['We are happy to see you subscribed!'], 'type': 'success', 'role' : 'base'})
                    return redirect(url_for("home"))
                except IntegrityError as e:
                    flash({'content' : ['You have already subscribed!'], 'type': 'danger', 'role' : 'base'})
                    return redirect(url_for("home"))
            else:
                response = []
                if not newstellerForm.full_name.data:
                    response.append(responses['fname'])
                if not newstellerForm.email.data:
                    response.append(responses['email'])
                if newstellerForm.email.data:
                    try:
                        validate_email(newstellerForm.email.data)
                    except EmailNotValidError as e:
                        response.append(responses['invalid_email'])

                flash({'content' : response, 'type' : 'danger', 'role' : 'form-news'})
                return redirect(url_for("home"))

    return render_template('home.html')

@app.route("/search/", methods = ['POST'])
def search():
    page = request.args.get('page', 1, type=int)
    if request.method == 'POST':
        if 'search' in request.form:
            keyword = SearchForm(request.form).keyword.data
            all_products = Product.query.filter( Product.name.like('%' + keyword + '%') ).paginate(page=page, per_page=PRODUCTS_PER_PAGE)

            return render_template('home.html', all_products = all_products)

@app.route("/category/<string:parent>/<string:child>", methods = ['GET', 'POST'])
def category(parent, child):    
    page = request.args.get('page', 1, type=int)

    if not parent == 'man-woman-unisex':
        parentid = Category.query.filter_by( name = parent ).first().id
        relations_parent = Categoryproductrel.query.filter_by(category_id = parentid).all()
        parent_products = [rel.product_id for rel in relations_parent]

        childs= Category.query.filter_by( name = child ).all()
        childids = [child.id for child in childs]
        relations_child = Categoryproductrel.query.filter(  Categoryproductrel.category_id.in_(childids) ).all()
        child_products = [rel.product_id for rel in relations_child]

        common_products = list(set(list(set(parent_products).intersection(child_products))))
        all_products = Product.query.filter(Product.id.in_(common_products)).paginate(page=page, per_page=PRODUCTS_PER_PAGE)

    else:
        childs= Category.query.filter_by( name = child ).all()
        childids = [child.id for child in childs]
        relations_child = Categoryproductrel.query.filter(  Categoryproductrel.category_id.in_(childids) ).all()
        child_products = [rel.product_id for rel in relations_child]
        all_products = Product.query.filter(Product.id.in_(child_products)).paginate(page=page, per_page=PRODUCTS_PER_PAGE)


    if request.method == 'POST' and 'newsteller' in request.form:
            newstellerForm = NewsTellerForm(request.form)
            if newstellerForm.validate_on_submit():
                subscriber = Newsletter (
                    full_name = newstellerForm.full_name.data,
                    email = newstellerForm.email.data,
                )
                try:
                    subscriber.save()
                    flash({'content' : ['We are happy to see you subscribed!'], 'type': 'success', 'role' : 'base'})
                    return redirect(url_for("category", parent = parent, child = child))
                except IntegrityError as e:
                    flash({'content' : ['You have already subscribed!'], 'type': 'danger', 'role' : 'base'})
                    return redirect(url_for("category", parent = parent, child = child))
            else:
                response = []
                if not newstellerForm.full_name.data:
                    response.append(responses['fname'])
                if not newstellerForm.email.data:
                    response.append(responses['email'])
                if newstellerForm.email.data:
                    try:
                        validate_email(newstellerForm.email.data)
                    except EmailNotValidError as e:
                        response.append(responses['invalid_email'])

                flash({'content' : response, 'type' : 'danger', 'role' : 'form-news'})
                return redirect(url_for("category", parent = parent, child = child))
    return render_template('home.html', all_products = all_products)

@app.route("/register/",  methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash({'content': 'You are already logged in! Log out to create a new account!', 'type': 'warning', 'role' : 'base'})
        return redirect(url_for("home"))
    registerForm = RegisterForm()

    if request.method == 'POST':
        if 'register' in request.form:
            registerForm = RegisterForm(request.form)
            if registerForm.validate_on_submit():
                user = User(
                    full_name = registerForm.full_name.data,
                    email = registerForm.email.data,
                    password = generate_password_hash(registerForm.password.data),
                    is_superuser = False
                )
                try:
                    user.save()
                    flash({'content' : ['You have successfully created a new user!'], 'type' : 'success', 'role' : 'base'})
                    return redirect(url_for('login'))
                except:
                    flash({'content' : ['This email address is in use!'], 'type' : 'danger', 'role' : 'form'})
                    return redirect(url_for('register'))
                
            else:
                response = []
                if not registerForm.full_name.data:
                   response.append(responses['fname'])
                if not registerForm.email.data:
                    response.append(responses['email'])
                if not registerForm.password.data:
                    response.append(responses['passwd'])         
                if not registerForm.password_confirmation.data:
                    response.append(responses['passwd_conf']) 
                if registerForm.password.data != registerForm.password_confirmation.data:
                    response.append(responses['unmatching_passwd'])
                
                flash({'content' : response, 'type' : 'danger', 'role' : 'form'})
                return redirect(url_for('register'))
    
        elif 'newsteller' in request.form:
            newstellerForm = NewsTellerForm(request.form)
            if newstellerForm.validate_on_submit():
                subscriber = Newsletter (
                    full_name = newstellerForm.full_name.data,
                    email = newstellerForm.email.data,
                )
                try:
                    subscriber.save()
                    flash({'content' : ['We are happy to see you subscribed!'], 'type': 'success', 'role' : 'base'})
                    return redirect(url_for("register"))
                except IntegrityError as e:
                    flash({'content' : ['You have already subscribed!'], 'type': 'danger', 'role' : 'base'})
                    return redirect(url_for("register"))
                    
            else:
                response = []
                if not newstellerForm.full_name.data:
                    response.append(responses['fname'])
                if not newstellerForm.email.data:
                    response.append(responses['email'])
                if newstellerForm.email.data:
                    try:
                        validate_email(newstellerForm.email.data)
                    except EmailNotValidError as e:
                        response.append(responses['invalid_email'])

                flash({'content' : response, 'type' : 'danger', 'role' : 'form-news'})
                return redirect(url_for("register"))
            
    return render_template('register.html', registerForm = registerForm)

@app.route("/login/", methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash({'content' : ['You are already logged in! Log out first to switch you account!'], 'type': 'danger', 'role' : 'base'})
        return redirect(url_for("home"))
    loginForm = LoginForm()

    if request.method == 'POST':
        if 'login' in request.form:
            user = User.query.filter_by( email = loginForm.email.data ).first()
            if user and check_password_hash(user.password, loginForm.password.data):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash({'content' : [responses['invalid_user']], 'type': 'danger', 'role' : 'form'})
                return redirect(url_for('login'))
        
        elif 'newsteller' in request.form:
            newstellerForm = NewsTellerForm(request.form)
            if newstellerForm.validate_on_submit():
                subscriber = Newsletter (
                    full_name = newstellerForm.full_name.data,
                    email = newstellerForm.email.data,
                )
                try:
                    subscriber.save()
                    flash({'content' : ['We are happy to see you subscribed!'], 'type': 'success', 'role' : 'base'})
                    return redirect(url_for("login"))
                except IntegrityError as e:
                    flash({'content' : ['You have already subscribed!'], 'type': 'danger', 'role' : 'base'})
                    return redirect(url_for("login"))
            else:
                response = []
                if not newstellerForm.full_name.data:
                    response.append(responses['fname'])
                if not newstellerForm.email.data:
                    response.append(responses['email'])
                if newstellerForm.email.data:
                    try:
                        validate_email(newstellerForm.email.data)
                    except EmailNotValidError as e:
                        response.append(responses['invalid_email'])

                flash({'content' : response, 'type' : 'danger', 'role' : 'form-news'})
                return redirect(url_for("login"))
    
    return render_template('login.html', loginForm = loginForm)

@app.route("/logout/")
def logout():
    if not current_user.is_authenticated:
        flash({'content' : ['You are not logged in!'], 'type': 'danger', 'role' : 'base'})
        return redirect(url_for("home"))
    logout_user()
    return redirect(url_for('home'))

@app.route("/favorites/", methods = ['GET', 'POST'])
def favorites():

    all_favorites = Favorites.query.filter_by(user_id = current_user.id).all()

    # Discounts
    product_ids = [favorite.product_id for favorite in all_favorites]

    discounts = Discounts.query.filter(Discounts.product_id.in_(product_ids)).all()
    discount_mapping = {}  
    for discount in discounts:
        discount_mapping[discount.product_id] = discount

    if request.method == 'POST' and 'newsteller' in request.form:
            newstellerForm = NewsTellerForm(request.form)
            if newstellerForm.validate_on_submit():
                subscriber = Newsletter (
                    full_name = newstellerForm.full_name.data,
                    email = newstellerForm.email.data,
                )
                try:
                    subscriber.save()
                    flash({'content' : ['We are happy to see you subscribed!'], 'type': 'success', 'role' : 'base'})
                    return redirect(url_for("favorites"))
                except IntegrityError as e:
                    flash({'content' : ['You have already subscribed!'], 'type': 'danger', 'role' : 'base'})
                    return redirect(url_for("favorites"))
            else:
                response = []
                if not newstellerForm.full_name.data:
                    response.append(responses['fname'])
                if not newstellerForm.email.data:
                    response.append(responses['email'])
                if newstellerForm.email.data:
                    try:
                        validate_email(newstellerForm.email.data)
                    except EmailNotValidError as e:
                        response.append(responses['invalid_email'])

                flash({'content' : response, 'type' : 'danger', 'role' : 'form-news'})
                return redirect(url_for("favorites"))

    return render_template('favorites.html', all_favorites = all_favorites, discount_mapping = discount_mapping)

@app.route("/contact/", methods = ['GET', 'POST'])
def contact():
    contactForm = ContactForm()
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
                flash({'content' : [responses['sent_message']], 'type': 'success', 'role' : 'base'})
                return redirect(url_for("contact"))

            else:
                response = []
                if not contactForm.full_name.data:
                    response.append(responses['fname'])
                if not contactForm.email.data:
                    response.append(responses['email'])
                if not contactForm.subject.data:
                    response.append(responses['subject'])         
                if not contactForm.message.data:
                    response.append(responses['message']) 
                if contactForm.email.data:
                    try:
                        validate_email(contactForm.email.data)
                    except EmailNotValidError as e:
                        response = [].append(responses['invalid_email'])
                flash({'content' : response, 'type': 'danger', 'role' : 'form'})
                return redirect(url_for("contact"))
            
        elif 'newsteller' in request.form:
            newstellerForm = NewsTellerForm(request.form)
            if newstellerForm.validate_on_submit():
                subscriber = Newsletter (
                    full_name = newstellerForm.full_name.data,
                    email = newstellerForm.email.data,
                )
                try:
                    subscriber.save()
                    flash({'content' : ['We are happy to see you subscribed!'], 'type': 'success', 'role' : 'base'})
                    return redirect(url_for("contact"))
                except IntegrityError as e:
                    flash({'content' : ['You have already subscribed!'], 'type': 'danger', 'role' : 'base'})
                    return redirect(url_for("contact"))
            else:
                response = []
                if not newstellerForm.full_name.data:
                    response.append(responses['fname'])
                if not newstellerForm.email.data:
                    response.append(responses['email'])
                if newstellerForm.email.data:
                    try:
                        validate_email(newstellerForm.email.data)
                    except EmailNotValidError as e:
                        response.append(responses['invalid_email'])

                flash({'content' : response, 'type' : 'danger', 'role' : 'form-news'})
                return redirect(url_for("contact"))
    
    return render_template('contact.html', contactForm = contactForm)

@app.route("/product/<int:id>", methods = ['GET', 'POST'])
def detail(id):
    # Discounts
    discount = Discounts.query.filter_by(product_id = id).first()

    # Reviews
    reviewForm = ReviewForm()
    reviews = Review.query.filter_by(product_id = id).all()

    # Recommended Product
    relations = Categoryproductrel.query.filter_by(product_id = id).all()
    category_ids = [rel.category_id for rel in relations]
    category_ids = list ( set(category_ids) )
    rec_relations = Categoryproductrel.query.filter(Categoryproductrel.category_id.in_(category_ids)).all()
    recommended_product_ids = [rr.product_id for rr in rec_relations]
    recommended_product_ids = list ( set(recommended_product_ids) )
    try:
        recommended_product_ids.remove(id)
    except:
        pass
    recommended_products = Product.query.filter(Product.id.in_(recommended_product_ids)).all()

    # Main Product
    product = Product.query.filter_by(id = id).first()

    is_favorite = False
    if  current_user.is_authenticated and Favorites.query.filter_by(user_id = current_user.id, product_id = id).first():
        is_favorite = True

    
    if request.method == 'POST' :
        if 'newsteller' in request.form:
            newstellerForm = NewsTellerForm(request.form)
            if newstellerForm.validate_on_submit():
                subscriber = Newsletter (
                    full_name = newstellerForm.full_name.data,
                    email = newstellerForm.email.data,
                )
                try:
                    subscriber.save()
                    flash({'content' : ['We are happy to see you subscribed!'], 'type': 'success', 'role' : 'base'})
                    return redirect(url_for("detail", id = id))
                except IntegrityError as e:
                    flash({'content' : ['You have already subscribed!'], 'type': 'danger', 'role' : 'base'})
                    return redirect(url_for("detail", id = id))
            else:
                response = []
                if not newstellerForm.full_name.data:
                    response.append(responses['fname'])
                if not newstellerForm.email.data:
                    response.append(responses['email'])
                if newstellerForm.email.data:
                    try:
                        validate_email(newstellerForm.email.data)
                    except EmailNotValidError as e:
                        response.append(responses['invalid_email'])

                flash({'content' : response, 'type' : 'danger', 'role' : 'form-news'})
                return redirect(url_for("detail", id = id))
        if 'review' in request.form:
            if not current_user.is_authenticated:
                flash({'content' : ['You have to be logged in to unlike a product!'], 'type': 'warning', 'role' : 'base'})
                return redirect(url_for('login'))
            else:
                if reviewForm.validate_on_submit():
                    reviewForm = ReviewForm(request.form)
                    review = Review(
                        content = reviewForm.content.data,
                        user_id = current_user.id,
                        product_id = id
                    )
                    review.save()
                    flash({'content' : ['Your review has been submitted!'], 'type' : 'success', 'role' : 'base'})
                    review = ReviewForm()
                    return redirect(url_for("detail", id = id))
                else:
                    flash({'content' : ['You have not filled the content box!'], 'type' : 'danger', 'role' : 'base'})
                    return redirect(url_for("detail", id = id))
    
    return render_template('detail.html', product = product, recommended_products = recommended_products, is_favorite = is_favorite, reviews = reviews, reviewForm = reviewForm, discount = discount)

@app.route("/add-favorite/<int:productid>")
def addfavorite(productid):
    if current_user.is_authenticated:
        favorite = Favorites.query.filter_by(product_id = productid, user_id = current_user.id).first()
        if favorite:
            flash({'content' : ['Product has been already added!'], 'type': 'danger', 'role' : 'base'})
            return redirect(url_for('detail', id = productid))  
        favorite = Favorites(
            user_id = current_user.id,
            product_id = productid
        )
        favorite.save()
        flash({'content' : ['Product has been added successfully!'], 'type': 'success', 'role' : 'base'})
        return redirect(url_for('detail', id = productid))
               
    else:
        flash({'content' : ['You have to be logged in to like a product!'], 'type': 'warning', 'role' : 'base'})
        return redirect(url_for('login'))

@app.route("/remove-favorite/<int:productid>")
def removefavorite(productid):
    if current_user.is_authenticated:
        referrer = request.referrer
        if referrer:
            if 'favorites' in referrer:
                favorite = Favorites.query.filter_by(product_id = productid, user_id = current_user.id).first()
                if favorite:
                        db.session.delete(favorite)
                        db.session.commit()
                        flash({'content' : ['Product has been removed successfully!'], 'type': 'success', 'role' : 'base'})
                        return redirect(url_for('favorites'))
                else:
                    flash({'content' : ['Product was not found in your faavorite list!'], 'type': 'danger', 'role' : 'base'})
                    return redirect(url_for('favorites'))
                
            elif 'detail' in referrer:
                favorite = Favorites.query.filter_by(product_id = productid, user_id = current_user.id).first()
                if favorite:
                        db.session.delete(favorite)
                        db.session.commit()
                        flash({'content' : ['Product has been removed successfully!'], 'type': 'success', 'role' : 'base'})
                        return redirect(url_for('detail', id=productid))
                else:
                    flash({'content' : ['Product was not found in your faavorite list!'], 'type': 'danger', 'role' : 'base'})
                    return redirect(url_for('detail', id=productid))
        
        favorite = Favorites.query.filter_by(product_id = productid, user_id = current_user.id).first()
        if favorite:
                db.session.delete(favorite)
                db.session.commit()
                flash({'content' : ['Product has been removed successfully!'], 'type': 'success', 'role' : 'base'})
                return redirect(url_for('favorites'))
        else:
            flash({'content' : ['Product was not found in your faavorite list!'], 'type': 'danger', 'role' : 'base'})
            return redirect(url_for('favorites'))
    else:
        flash({'content' : ['You have to be logged in to unlike a product!'], 'type': 'warning', 'role' : 'base'})
        return redirect(url_for('login'))
