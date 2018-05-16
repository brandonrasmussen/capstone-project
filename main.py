from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask.ext.mail import Message, Mail 
import os

# Flask-WTF
from flask_wtf import Form 
from wtforms import TextField, PasswordField, validators, HiddenField, TextAreaField, BooleanField, SelectField, DateField, IntegerField, RadioField
from wtforms.validators import Required, EqualTo, Optional, AnyOf
from wtforms.validators import Length, email
from wtforms.fields.html5 import DateField

# Hash Passwords
from werkzeug.security import generate_password_hash, check_password_hash

# Handle Login
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

mail = Mail()

app = Flask(__name__)

app.config['DEBUG'] = True 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://capstone-project:password@localhost:8889/capstone-project'
app.config['SQLALCHEMY_ECHO'] = True 

app.config['CSRF_ENABLED'] = True 
app.config['SECRET_KEY'] = 'pie'

# Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'brandonrasmussen2@gmail.com'
app.config['MAIL_PASSWORD'] = 'Brookie2'

mail.init_app(app)

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
            email(message=(u'That\'s not a valid email address.'))])
    password = PasswordField('Password', validators=[
            Required(),
            Length(min=6, message=(u'Password needs to be a minimum of six characters'))])

# Class for Login WTForm Fields
class LoginForm(Form):
    email = TextField('Email Address', validators=[
            Required('Please provide a valid email address'),
            email(message=(u'That\'s not a valid email address.'))])
    password = PasswordField('Password', validators=[
            Required('Please provide a valid password')])

# Class for Contact WTForm Fields
class ContactForm(Form):
    tell = SelectField(u'What would you like to tell us about?', choices=[('none', 'Please select one'), ('Restaurant/Food Experience', 'Restaurant/Food Experience'), ('Website', 'Website'),
            ('General Inquiry', 'General Inquiry')], validators =[AnyOf(values=['Restaurant/Food Experience', 'Website', 'General Inquiry'], message='Please select an option')])
    order = SelectField(u'How did you order?', choices=[('none', 'Please select one'), ('Online', 'Online'), ('Telephone', 'Telephone'), ('Dine-In', 'Dine-In')], 
    validators =[AnyOf(values=['Online', 'Telephone', 'Dine-In'], message='Please select an option')])
    time = SelectField(u'Time', choices=[('none', 'Please select one'), ('Lunch', 'Lunch (Before 2pm)'), ('Midday', 'Midday (2pm-5pm)'), ('Dinner', 'Dinner (5pm-8pm'),
            ('Late', 'Late Night (After 8pm)')], validators =[AnyOf(values=['Lunch', 'Midday', 'Dinner', 'Late'], message='Please select an option')])
    date = DateField('Date', format='%Y-%m-%d')
    amount = TextField('Total Amount', validators=[Required('Please provide the amount of your order')])
    share = SelectField(u'Did you share your feedback with the restaurant?', choices=[('none', 'Please select one'), ('Yes', 'Yes'), ('No', 'No')],
    validators =[AnyOf(values=['Yes', 'No'], message='Please select an option')])
    message = TextAreaField('Message', validators=[Required('Please provide a message')])
    response = RadioField ('How would you like us to get back to you?', choices=[('Email', 'Email'), ('Phone', 'Telephone'), ('None', 'No Response Needed')])
    firstName = TextField('First Name', validators=[Required('Please provide your first name')])
    lastName = TextField('Last Name', validators=[Required('Please provide your last name')])
    email = TextField('Email Address', validators=[Required('Please provide your email address'),
    email(message=(u'That\'s not a valid email address.'))])
    confirmEmail = TextField('Confirm Address', validators=[EqualTo('email', message='Email does not match')])
    phone = TextField('Telphone Number', validators=[Required('Please provide a telephone number')])
    address = TextField('Address', validators=[Required('Please provide an address')])
    city = TextField('City', validators=[Required('Please provide a city')])
    state = TextField('State', validators=[Required('Please provide a state')])
    postal = TextField('Zip Code', validators=[Required('Please provide a zip code')])

# Class for Menu WTForm Fields
class Menu(Form):
    hippie = RadioField(choices=[('Small', 'Small'), ])
    
@app.route('/')
def homepage():
    return render_template('index.html', title='Fun House Pizza')

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    return render_template('menu.html', title='Menu')

@app.route('/companyinfo')
def info():
    return render_template('companyinfo.html', title='Company Information')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('contact.html', form=form, title='Contact Us')
        else:
            msg = Message(form.tell.data, sender='brandonrasmussen2@gmail.com', recipients=['brandonrasmussen2@gmail.com'])
            msg.body = """ 
            From: %s %s <%s>

            How was it ordered: %s
            Time: %s 
            Date: %s
            Amount of order: %s
            Share Feedback: %s

            Message: %s

            Response Needed: %s

            Contact Info
            E-mail Address: %s
            Telephone Number: %s
            Address: %s
            City: %s
            State: %s
            Zip Code: %s


            """ %(form.firstName.data,form.lastName.data, form.email.data, form.order.data, form.time.data, form.date.data, form.amount.data,
                form.share.data,form.message.data, form.response.data, form.email.data, form.phone.data, form.address.data, form.city.data, form.state.data,
                form.postal.data)
            mail.send(msg)
            return render_template('contact.html', success=True)
    elif request.method == 'GET':
        return render_template('contact.html', form=form, title='Contact Us')

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