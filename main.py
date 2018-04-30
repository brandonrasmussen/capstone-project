from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

# Flask-WTF
from flask_wtf import Form 
from wtforms import TextField, PasswordField, validators, HiddenField
from wtforms import TextAreaField, BooleanField
from wtforms.validators import Required, EqualTo, Optional
from wtforms.validators import Length, email

# Hash Passwords
from werkzeug.security import generate_password_hash, check_password_hash

# Handle Login
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['DEBUG'] = True 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://capstone-project:password@localhost:8889/capstone-project'
app.config['SQLALCHEMY_ECHO'] = True 

app.config['CSRF_ENABLED'] = True 
app.config['SECRET_KEY'] = 'pie'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    productName = db.Column(db.String(120))
    productDescription = db.Column(db.String(120))
    unitPrice = db.Column(db.Numeric(3,2))
    categoryID = db.Column(db.Integer, db.ForeignKey('category.id'))

    def __init__(self, productName, productDescription, unitPrice, category):
        self.productName = productName
        self.productDescription = productDescription
        self.unitPrice = unitPrice
        self.category = category 

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoryName = db.Column(db.String(120))

    def __init__(self, categoryName):
        self.categoryName = categoryName

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.column(db.DateTime) 
    customerID = db.Column(db.Integer, db.ForeignKey('category.id'))

    def __init__(self, timestamp,customer):
        self.timestamp = timestamp
        self.customer = customer

class OrderDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(20))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Numeric(3,2))
    total = db.Column(db.Numeric(3,2))
    orderID = db.Column(db.Integer, db.ForeignKey('orders.id'))
    productID = db.Column(db.Integer, db.ForeignKey('products.id'))

    def __init__(self, size, quantity, price, total, order, product):
        self.size = size
        self.quantity = quantity
        self.price = price
        self.total = total
        self.order = order
        self.product = product

class Customers(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(30))
    lastName = db.Column(db.String(30))
    address = db.Column(db.String(50))
    apartmentNumber = db.Column(db.Integer)
    city = db.Column(db.String(20))
    state = db.Column(db.String(20))
    postalCode = db.Column(db.Integer)
    phone = db.Column(db.String(10))
    email = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(80))

    def __init__(self, firstName = None, lastName = None, address = None, apartmentNumber = None, 
        city = None, state = None, postalCode= None, phone = None, email = None, password = None):
        self.firstName = firstName
        self.lastName = lastName
        self.address = address
        self.apartmentNumber = apartmentNumber
        self.city = city
        self.state = state
        self.postalCode = postalCode
        self.phone = phone
        self.email = email
        self.password = password
        orders = db.relationship('Orders', backref='customers')

@login_manager.user_loader
def load_user(customer_id):
    return Customers.query.get(int(customer_id))

# Class for Signup WTForm Fields
class SignupForm(Form):
    firstName = TextField('First Name', validators=[
            Required('Please provide your first name')])
    lastName = TextField('Last Name', validators=[
            Required('Please provide your last name')])
    address = TextField('Address', validators=[
            Required('Please provide an address')])
    apartmentNumber = TextField('Apartment Number')
    city = TextField('City', validators=[
            Required('Please provide a city')])
    state = TextField('State', validators=[
            Required('Please provide a state')])
    postalCode = TextField('Zip Code', validators=[
            Required('Please provide a zip code')])
    phone = TextField('Phone Number', validators=[
            Required('Please provide a phone number')])
    email = TextField('Email Address', validators=[
            Required('Please provide a valid email address'),
            Length(min=6, message=(u'Email address too short')),
            email(message=(u'That\'s not a valid email address.'))])
    password = PasswordField('Password', validators=[
            Required(),
            Length(min=6, message=(u'Password needs to be a minimum of six characters'))])

# Class for Login WTForm Fields
class LoginForm(Form):
    email = TextField('Email Address', validators=[
            Required('Please provide a valid email address')])
    password = PasswordField('Password', validators=[
            Required('Please provide a valid password')])

@app.route('/')
def homepage():
    return render_template('index.html', title='Fun House Pizza')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/companyinfo')
def info():
    return render_template('companyinfo.html', title='Company Information')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method =='POST':
        form = SignupForm(request.form)

        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            customer = Customers(firstName=form.firstName.data, lastName=form.lastName.data, address=form.address.data, 
            apartmentNumber=form.apartmentNumber.data, city=form.city.data, state=form.state.data, postalCode=form.postalCode.data,
            phone=form.phone.data, email=form.email.data, password=hashed_password)
            email_exist = Customers.query.filter_by(email=form.email.data).first()
            if email_exist:
                form.email.errors.append('An account with that email address already exists')
                return render_template('signup.html', form = form, title = "Signup for Account")
            else:
                db.session.add(customer)
                db.session.commit()
                return render_template('index.html', customer = customer)
        else: 
            return render_template('signup.html', form = form, title = "Signup for Account")
    return render_template('signup.html', form = SignupForm(), title = "Signup for Account")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email_exist = Customers.query.filter_by(email=form.email.data).first()
        user = Customers.query.filter_by(email=form.email.data).first()

        if not email_exist:
            form.email.errors.append('There is not an account with this email')
        elif user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return render_template('index.html', title ="Login")
    return render_template('login.html', form=form, title ="Login")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('index.html')

if __name__ == '__main__':
    app.run()