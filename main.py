from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy 

# Flask-WTF
from flask.ext.wtf import Form 
from wtforms import TextField, PasswordField, validators, HiddenField
from wtforms import TextAreaField, BooleanField
from wtforms.validators import Requred, EqualTo, Optional
from wtforms.validators import Length, email

app = Flask(__name__)
app.config['DEBUG'] = True 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://capstone-project:password@localhost:8889/capstone-project'
app.config['SQLALCHEMY_ECHO'] = True 

app.config['CSRF_ENABLED'] = True 
app.config['SECRET_KEY'] = 'pie'

db = SQLAlchemy(app)


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

class Customers(db.Model):
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
    password = db.Column(db.String(20))

    def __init__(self, firstName, lastName, address, apartmentNumber, city, state, postalCode, phone, 
        email, password):
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



@app.route('/')
def homepage():
    return render_template('index.html', title='Fun House Pizza')

@app.route('/menu')
def display():
    return render_template('menu.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method =='POST':
        form = SignupForm(request.form)
        if form.validate():
            pass
        else: 
            return render_template('signup.html', form = form, title = "Signup for Account")
    return render_template('signup.html', form = SignupForm(), title = "Signup for Account")


if __name__ == '__main__':
    app.run()