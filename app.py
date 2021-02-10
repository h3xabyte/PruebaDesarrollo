from flask import Flask, request, jsonify, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps
import sqlite3
import csv

app = Flask(__name__)

app.config['SECRET_KEY']='Th1s1ss3cr3t'
app.config['SQLALCHEMY_DATABASE_URI']=r'sqlite:///C:\Users\HP\Desktop\qck\quick.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
conn = sqlite3.connect('quick.db', check_same_thread=False)

class Users(db.Model):
     __tablename__ = 'usuarios'
     id = db.Column(db.Integer, primary_key=True)
     public_id = db.Column(db.Integer)
     name = db.Column(db.String(50))
     password = db.Column(db.String(50))
     admin = db.Column(db.Boolean)


class Clients(db.Model):
     __tablename__ = 'clients'
     id = db.Column(db.Integer, primary_key=True)
     document = db.Column(db.String(50), unique=True, nullable=False)
     first_name = db.Column(db.String(20), unique=True, nullable=False)
     last_name = db.Column(db.String(50), nullable=False)
     email = db.Column(db.String(50), nullable=False)


class Bills(db.Model):
     __tablename__ = 'bills'
     id = db.Column(db.Integer, primary_key=True)
     client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
     company_name = db.Column(db.String(50), unique=True, nullable=False)
     nit = db.Column(db.String(20), unique=True, nullable=False)
     code = db.Column(db.String(50), nullable=False)


class Products(db.Model):
     __tablename__ = 'products'
     id = db.Column(db.Integer, primary_key=True)
     name = db.Column(db.String(50), unique=True, nullable=False)
     description = db.Column(db.String(20), unique=True, nullable=False)
     att4 = db.Column(db.String(50), nullable=False)


class Billsproducts(db.Model):
     __tablename__ = 'bills-products'
     id = db.Column(db.Integer, primary_key=True)
     bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'))
     product_id = db.Column(db.Integer, db.ForeignKey('products.id'))



def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):

      token = None

      if 'x-access-tokens' in request.headers:
         token = request.headers['x-access-tokens']

      if not token:
         return jsonify({'message': 'a valid token is missing'})


      data = jwt.decode(token, 'secret')
      current_user = Users.query.filter_by(public_id=data['public_id']).first()
      return f(current_user, *args, **kwargs)



   return decorator




@app.route('/register', methods=['GET', 'POST'])
def signup_user():
 data = request.get_json()

 hashed_password = generate_password_hash(data['password'], method='sha256')

 new_user = Users(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
 db.session.add(new_user)
 db.session.commit()

 return jsonify({'message': 'registered successfully'})




@app.route('/login', methods=['GET', 'POST'])
def login_user():

  auth = request.authorization

  if not auth or not auth.username or not auth.password:
     return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

  user = Users.query.filter_by(name=auth.username).first()

  if check_password_hash(user.password, auth.password):
     token = jwt.encode({'public_id': user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, 'secret')
     return jsonify({'token' : token.decode('UTF-8')})

  return make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})



@app.route('/users', methods=['GET'])
def get_all_users():

   users = Users.query.all()

   result = []

   for user in users:
       user_data = {}
       user_data['public_id'] = user.public_id
       user_data['name'] = user.name
       user_data['password'] = user.password
       user_data['admin'] = user.admin

       result.append(user_data)

   return jsonify({'users': result})



#Crear Clientes
@app.route('/client', methods=['POST', 'GET'])
@token_required
def create_client(current_user):

   data = request.get_json()

   new_clients = Clients(document=data['document'], first_name=data['first_name'], last_name=data['last_name'], email=data['email'])
   db.session.add(new_clients)
   db.session.commit()

   return jsonify({'message' : 'nuevo cliente creado'})


#Obtener Clientes
@app.route('/client-get', methods=['POST', 'GET'])
@token_required
def get_clients(current_user):

    clientes= Clients.query.all()

    output = []
    for cliente in clientes:

           cliente_data = {}
           cliente_data['id'] = cliente.id
           cliente_data['document'] = cliente.document
           cliente_data['first_name'] = cliente.first_name
           cliente_data['last_name'] = cliente.last_name
           cliente_data['email'] = cliente.email

           output.append(cliente_data)

    return jsonify({'list_of_clients' : output})



#Update Clientes
@app.route('/client/<client_id>/<first_name>/<last_name>/<email>', methods=['PUT'])
@token_required
def update_client(current_user, client_id, first_name, last_name, email):
    cliente = Clients.query.filter_by(document=client_id).first()
    if not cliente:
       return jsonify({'message': 'client does not exist'})


    cliente.first_name = first_name
    cliente.last_name = last_name
    cliente.email = email

    db.session.commit()

    return jsonify({'message': 'Client updated'})



#Delete Clientes
@app.route('/client/<client_id>', methods=['DELETE'])
@token_required
def delete_client(current_user, client_id):
    print(client_id)
    client = Clients.query.filter_by(document=client_id).first()
    if not client:
       return jsonify({'message': 'client does not exist'})


    db.session.delete(client)
    db.session.commit()

    return jsonify({'message': 'Client deleted'})



#Crear Bills
@app.route('/bill', methods=['POST', 'GET'])
@token_required
def create_bill(current_user):

   data = request.get_json()

   new_bills = Bills(client_id=data['client_id'], company_name=data['company_name'], nit=data['nit'], code=data['code'])
   db.session.add(new_bills)
   db.session.commit()

   return jsonify({'message' : 'nueva factura creada'})



#Obtener Facturas
@app.route('/bills-get', methods=['POST', 'GET'])
@token_required
def get_bills(current_user):

    bills= Bills.query.all()

    output = []
    for bill in bills:

           bill_data = {}
           bill_data['id'] = bill.id
           bill_data['client_id'] = bill.client_id
           bill_data['company_name'] = bill.company_name
           bill_data['nit'] = bill.nit
           bill_data['code'] = bill.code

           output.append(bill_data)

    return jsonify({'list_of_bills' : output})



#Update Bills
@app.route('/bill/<bill_id>/<client_id>/<company_name>/<nit>/<code>', methods=['PUT'])
@token_required
def update_bill(current_user, bill_id, client_id, company_name, nit, code):
    bill = Bills.query.filter_by(id=bill_id).first()
    if not bill:
       return jsonify({'message': 'bill does not exist'})


    bill.client_id = client_id
    bill.company_name = company_name
    bill.nit = nit
    bill.code = code

    db.session.commit()

    return jsonify({'message': 'Bill updated'})



#Delete Bills
@app.route('/bill/<bill_id>', methods=['DELETE'])
@token_required
def delete_bills(current_user, bill_id):
    print(bill_id)
    bill = Bills.query.filter_by(id=bill_id).first()
    if not bill:
       return jsonify({'message': 'bill does not exist'})


    db.session.delete(bill)
    db.session.commit()

    return jsonify({'message': 'bill deleted'})



#Crear Products
@app.route('/product', methods=['POST', 'GET'])
@token_required
def create_product(current_user):

   data = request.get_json()

   new_product = Products(name=data['name'], description=data['description'], att4=data['att4'])
   db.session.add(new_product)
   db.session.commit()

   return jsonify({'message' : 'nuevo producto creado'})



#Obtener Productos
@app.route('/products-get', methods=['POST', 'GET'])
@token_required
def get_products(current_user):

    products= Products.query.all()

    output = []
    for product in products:

           product_data = {}
           product_data['id'] = product.id
           product_data['name'] = product.name
           product_data['description'] = product.description
           product_data['att4'] = product.att4


           output.append(product_data)

    return jsonify({'list_of_products' : output})



#Update Products
@app.route('/product/<product_id>/<name>/<description>/<att4>', methods=['PUT'])
@token_required
def update_product(current_user, product_id, name, description, att4):
    product = Products.query.filter_by(id=product_id).first()
    if not product:
       return jsonify({'message': 'product does not exist'})


    product.name= name
    product.description = description
    product.att4 = att4


    db.session.commit()

    return jsonify({'message': 'Product updated'})



#Delete product
@app.route('/product/<product_id>', methods=['DELETE'])
@token_required
def delete_products(current_user, product_id):
    print(product_id)
    product = Products.query.filter_by(id=product_id).first()
    if not product:
       return jsonify({'message': 'product does not exist'})


    db.session.delete(product)
    db.session.commit()

    return jsonify({'message': 'product deleted'})



#Crear Bills-products
@app.route('/bproduct', methods=['POST', 'GET'])
@token_required
def create_bproduct(current_user):

   data = request.get_json()

   new_bproduct = Billsproducts(bill_id=data['bill_id'], product_id=data['product_id'])
   db.session.add(new_bproduct)
   db.session.commit()

   return jsonify({'message' : 'nuevo bill-producto creado'})



#Obtener Bills-Products
@app.route('/bproducts-get', methods=['POST', 'GET'])
@token_required
def get_bproducts(current_user):

    bproducts= Billsproducts.query.all()

    output = []
    for bproduct in bproducts:

           bproduct_data = {}
           bproduct_data['id'] = bproduct.id
           bproduct_data['bill_id'] = bproduct.bill_id
           bproduct_data['product_id'] = bproduct.product_id



           output.append(bproduct_data)

    return jsonify({'list_of_bills-products' : output})



#Update Bills-Products
@app.route('/bproduct/<bp_id>/<bill_id>/<product_id>', methods=['PUT'])
@token_required
def update_bproduct(current_user, bp_id, bill_id, product_id):
    bproduct = Billsproducts.query.filter_by(id=bp_id).first()
    if not bproduct:
       return jsonify({'message': 'Bproduct does not exist'})


    bproduct.bill_id= bill_id
    bproduct.product_id = product_id



    db.session.commit()

    return jsonify({'message': 'BProduct updated'})



#Delete bproduct
@app.route('/bproduct/<bproduct_id>', methods=['DELETE'])
@token_required
def delete_bproducts(current_user, bproduct_id):

    bproduct = Billsproducts.query.filter_by(id=bproduct_id).first()
    if not bproduct:
       return jsonify({'message': 'bproduct does not exist'})


    db.session.delete(bproduct)
    db.session.commit()

    return jsonify({'message': 'bproduct deleted'})



#descargar csv cliente
@app.route('/csv/<cliente>', methods=['GET'])
@token_required
def csvdownload(current_user, cliente):
    #limpiar resultado de cursores
    def limpiar(entrada):
        print(entrada)
        res = str(entrada)
        res = res.replace('[(', '').replace(',)]', '').replace('(', '').replace(')', '').replace("'", "").replace(",", "")
        return res


    cur1 = conn.cursor()
    cur2 = conn.cursor()
    cur3 = conn.cursor()
    cur4 = conn.cursor()

    cur3.execute('SELECT first_name FROM Clients WHERE document=?', (cliente,))
    nombre = cur3.fetchall()
    nombre =  ', '.join(map(str, nombre))
    nombre = limpiar(nombre)


    cur4.execute('SELECT last_name FROM Clients WHERE document=?', (cliente,))
    apellido = cur4.fetchall()
    apellido =  ', '.join(map(str, apellido))
    apellido = limpiar(apellido)


    cur1.execute('SELECT Id FROM Clients WHERE document=?', (cliente,))
    client_id = cur1.fetchall()
    client_id = limpiar(client_id)


    cur2.execute('SELECT COUNT(id) FROM Bills WHERE client_id=?', (client_id))
    numero = cur2.fetchall()
    numero = limpiar(numero)

    print(nombre, apellido, numero)


    with open('clients.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["nombre", "apellido", "numero-de-bills"])
        writer.writerow([nombre, apellido, numero])
    path = "clients.csv"
    return send_file(path, as_attachment=True)




#subir csv y crear clientes
@app.route('/uploader', methods = ['GET', 'POST'])
@token_required
def upload_file(current_user):
   if request.method == 'POST':
       f = request.files['file']
       if   f.filename != '':
            f.save(f.filename)
       with open(f.filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    print(f'Las columnas son {", ".join(row)}')
                    line_count += 1
                else:
                    print(row[0], row[1], row[2], row[3])
                    line_count += 1
                    new_clients = Clients(document=row[0], first_name=row[1], last_name=row[2], email=row[3])
                    db.session.add(new_clients)
                    db.session.commit()

   return jsonify({'message' : 'usuarios por csv creados'})

if  __name__ == '__main__':
     app.run(debug=True)