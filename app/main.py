from flask import Flask,request,jsonify,redirect,url_for,session
import json
from database_service import Product,Sales,db,app,User,Payment
from datetime import datetime
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager,create_access_token,jwt_required,get_jwt_identity
from sqlalchemy import text
from mpesa import make_stk_push
from extensions import app, db

import re

app.config["JWT_SECRET_KEY"] = "MyKey@123"

jwt = JWTManager(app)

bcrypt =Bcrypt(app)


# app = Flask(__name__)
CORS(app)
 
@app.route("/")
def hello():
    res ={"Flask-Api": "1.0"}
    return jsonify(res),200

@app.route("/api/products",methods = ["GET","POST"])
@jwt_required()
def products():
    email = get_jwt_identity()
    print("Email---------->",email)
    if request.method == "GET":
        product_list = Product.query.all()
        print('product List',product_list)

        prods =[]
        for i in product_list:
            product_data = {
                'id': i.id,
                'name': i.name,
                'buying_price': i.buying_price,
                'selling_price': i.selling_price
    
            }
            prods.append(product_data)
            
        
        # return a list of products as json
        return jsonify(prods),200
    elif request.method == "POST":
        #  Data will be received here as json so we convert it to dictionary
         data = dict(request.get_json())
         if "name" not in data.keys() or "buying_price" not in data.keys() or "selling_price" not in data.keys():
             error ={"error": "invalid keys"}
             return jsonify(error),403
         elif data["name"] == "" or data["buying_price"] == "" or data["selling_price"] == "":
             error ={"error": "ensure all values are set"}
             return jsonify(error),403
         else:
             new_product = Product(name=data["name"],buying_price= data["buying_price"],selling_price = data["selling_price"])
             db.session.add(new_product)
             db.session.commit()
             return jsonify(data),201
    else:
        # a different method was sent 
        error ={"error": "Method not allowed"}
        return jsonify(error),405  
    

@app.route("/api/sales",methods = ["GET","POST"])
@jwt_required()
def sales():
    if request.method == "GET": 
        sales_list = db.session.query(
        Sales.id.label('sale_id'),
        Product.name.label('product_name'),
        Product.selling_price.label('product_sp'),
        Sales.quantity.label('sale_quantity'), 
        Payment.trans_code.label('trans_code'),
        Sales.created_at
        ).join(Product, Sales.pid == Product.id).outerjoin(Payment, Sales.id == Payment.sale_id).all()
        print("Sale list ------", sales_list)
        sales_data = []
        for sale in sales_list:
            sale_info = {
                'sale_id': sale.sale_id,'product_name': sale.product_name,
                'product_sp' : sale.product_sp,'sale_quantity' : sale.sale_quantity, 
                'trans_code' : sale.trans_code,
                'amount': int(sale.sale_quantity * sale.product_sp),'created_at': sale.created_at
            }
            sales_data.append(sale_info)
        return jsonify(sales_data), 200
    elif request.method == "POST":
        #  Data will be received here as json so we convert it to dictionary
         data = dict(request.get_json())
         print("DATA::",data)
         if "pid" not in data.keys() or "quantity" not in data.keys() :
             error ={"error": "invalid keys"}
             return jsonify(error),403
         
         elif data["pid"] == "" or data["quantity"] == "":
             error ={"error": "ensure all values are set"}
             return jsonify(error),403
         
         else:
             if 'created_at' in data and data['created_at'] != "":
                print("Inside here!!")
                try:
                    created_at = datetime.strptime(data['created_at'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    error = {"error": "Invalid date format"}
                    return jsonify(error), 403
             else:
                    print("Inside Else!!") 
                    created_at = datetime.now()
             new_sale = Sales(pid=data["pid"],quantity= data["quantity"],created_at= created_at)
             db.session.add(new_sale)
             db.session.commit()
             
             return jsonify(data),201
    else:
        # a different method was sent 
        error ={"error": "Method not allowed"}
        return jsonify(error),405
    


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Check required fields
    if not data or "full_name" not in data or "email" not in data or "password" not in data:
        return jsonify({"error": "full_name, email, and password are required"}), 400

    full_name = data["full_name"]
    email = data["email"]
    password = data["password"]

    # Validate non-empty fields
    if not full_name or not email or not password:
        return jsonify({"error": "All fields must be non-empty"}), 400


    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    # Save user with plain password 
    new_user = User(full_name=full_name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Check required fields
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "email and password are required"}), 400

    email = data["email"]
    password = data["password"]

    # Validate non-empty fields
    if not email or not password:
        return jsonify({"error": "Email and password cannot be empty"}), 400

    user = User.query.filter_by(email=email, password=password).first()

    if user:
        # create token and return to the user
        token = create_access_token(identity=email)
        return jsonify({"message": "Login successful", "token": token}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401
    

@app.route("/api/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    email = get_jwt_identity()
    # print("Email (dashboard) ===", email)

    # Query: Profit per product
    profit_product = db.session.execute(text("""
        SELECT p.name, 
                SUM((p.selling_price - p.buying_price) * s.quantity) AS profit
        FROM sales s
        JOIN products p ON s.pid = p.id
        GROUP BY p.id
    """)).fetchall()

    # Query: Sales per day
    sales_day = db.session.execute(text("""
        SELECT DATE(s.created_at) AS date,
               SUM(p.selling_price * s.quantity) AS sales
        FROM sales s
        JOIN products p ON s.pid = p.id
        GROUP BY date
        ORDER BY date
    """)).fetchall()

    # Function to generate colors dynamically
    def generate_colors(n):
        colors = []
        for i in range(n):
            hue = int(360 * i / n)  # evenly space hues
            colors.append(f"hsl({hue}, 70%, 50%)")
        return colors
    

     # Format for frontend
    products_name = [row[0] for row in profit_product]

    products_sales = [float(row[1]) for row in profit_product]

    # Generate as many colors as products
    products_colour = generate_colors(len(profit_product))

    # Format sales per day
    dates = [row[0].strftime("%Y-%m-%d") for row in sales_day]
    sales = [float(row[1]) for row in sales_day]
    
    data = {
    "profit_per_product": {
        "products_name": products_name,
        "products_sales": products_sales,
        "products_colour": products_colour
    },
    "sales_per_day": {
        "dates": dates,
        "sales": sales
    }
}

    return jsonify(data), 200



## Payment Routes
@app.route("/api/payments", methods=["GET"])
@jwt_required()
def payments():
    ## Create a SQLAlchemy Model with fields -id,sale_id,amount,trans_code, created_at
    ## Get request only to get payments
    if request.method == "GET":
        payments_list = Payment.query.all()
        payments_data = []
        for payment in payments_list:
            payment_info = {
                'id': payment.id,
                'sale_id': payment.sale_id,
                'mrid' : payment.mrid,
                'crid' : payment.crid,
                'amount': payment.amount,
                'trans_code': payment.trans_code,
                'created_at': payment.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            payments_data.append(payment_info)
        return jsonify(payments_data), 200
    else:
        return jsonify({"error": "Method not allowed"}), 405


@app.route("/api/stkpush", methods=["POST"])
def stk_push():
    ## Get data from vue app to send stk push to M-pesa
    data = request.get_json()
    # store the mrid,crid,sale_id

    if "amount" not in data.keys() or "phone_number" not in data.keys() or "sale_id" not in data.keys():
        error ={"error" :" invalid keys"}
        return jsonify(error), 403
    res = make_stk_push(data["amount"],data["phone_number"],data["sale_id"])
    mrid = res["MerchantRequestID"]
    crid = res["CheckoutRequestID"]
    sale_id = data["sale_id"]

    #Create a record in payments table here
    pay = Payment(mrid= mrid, crid=crid,sale_id = sale_id)
    db.session.add(pay)
    db.session.commit()

    return json.dumps(res)

@app.route("/mpesa/callback", methods=["GET","POST"])
def mpesa_callback():
    ## Handle mpesa callback
    data  = request.get_json()
    print("STK DATA --------------------",data)

    mrid = data['Body']['stkCallback']['MerchantRequestID']
    crid = data['Body']['stkCallback']['CheckoutRequestID']

    #Filter your database to get the recored stored during callback by mrid,crid
    pay = Payment.query.filter_by(mrid=mrid, crid=crid).first()

    if int(data['Body']['stkCallback']['ResultCode']) == 0:
        #update the pay object
        trans_code = data['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value']
        amount = data['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value']
        pay.trans_code = trans_code
        pay.amount = amount
        db.session.commit()
        #phone_paid = data['Body']['stkCallback']['Item'][-1]['Value']
    else:
       pass
    
    return jsonify({"success" : "Callback received"}), 200

@app.route("/api/checker/<sale_id>")
def checker(sale_id):
    payment = Payment.query.filter_by(sale_id=sale_id).first
    return jsonify({"transaction_Code": payment.trans_code}), 200


  

if __name__ =="__main__":
    with app.app_context():
        # db.drop_all() 
        db.create_all() 

    app.run(debug=True)  
             
             