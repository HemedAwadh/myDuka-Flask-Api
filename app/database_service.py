from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime


# initialize the app
app = Flask(__name__)

#set up database conn
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:admin@localhost:5432/flask_api'

# disable events tracks object changes
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True

app.config['SQLALCHEMY_ECHO'] = True

#bind sqlalchemy to our flask application
db=SQLAlchemy(app)

#create models
#products model

class Product(db.Model):
    __tablename__ ='products'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,nullable=False)
    buying_price = db.Column(db.Float,nullable=False)
    selling_price = db.Column(db.Float,nullable=False)

    # sales =db.relationship('Sale',backref ='product')

class Sales(db.Model):
    __tablename__ ='sales'
    id=db.Column(db.Integer,primary_key=True)
    pid=db.Column(db.Integer,db.ForeignKey('products.id'),nullable=False)
    quantity = db.Column(db.Integer,nullable=False)
    created_at = db.Column(db.DateTime,nullable=False) 

class User(db.Model):
    __tablename__ = 'users'   
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Define the Payment model
class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, nullable=False)
    mrid = db.Column(db.String(100), nullable=False)
    crid = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=True)
    trans_code = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
   




      



     