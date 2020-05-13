from flask import Flask, Response, jsonify, request
from flask_mysqldb import MySQL
import jwt
import datetime
from secret import mysql_password, secret_key
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'flask'
app.config['MYSQL_PASSWORD'] = mysql_password
app.config['MYSQL_DB'] = 'drugs4nerdz'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = secret_key

mysql = MySQL(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = request.headers.get('Authorization').split("Bearer ")[1]
            jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'status': False, 'msg': 'Token is not valid!'}), 400
        return f(*args, **kwargs)
    return decorated

@app.route('/user/authenticate')
@token_required
def auth():
    token = request.headers.get('Authorization').split("Bearer ")[1]
    data = jwt.decode(token, app.config['SECRET_KEY'])
    return jsonify({'status': True, 'msg': 'Token is valid!', 'username': data['user']})

@app.route('/user/login', methods=['POST'])
def login():
    try:
        username = request.json['username']
        password = request.json['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        if bool(user):
            token = jwt.encode({'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'])
            return jsonify({'status': True, 'token': token.decode('UTF-8'), 'msg': "Welcome!"})
        return jsonify({'status': False, 'msg': 'User not found!'}), 404
    except:
        return jsonify({'status': False, 'msg': 'Please insert username and password in the body'}), 403

@app.route('/user/register', methods=['POST'])
def register():
    try:
        username = request.json['username']
        password = request.json['password']
        email = request.json['email']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username='" + username + "'")
        user = cursor.fetchone()
        cursor.close()
        if bool(user):
            return jsonify({'status': False, 'msg': 'Username is taken!'})
        else:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO users(username, email, password) VALUES(%s, %s, %s)", (username, email, password))
            mysql.connection.commit()
            cursor.close()
            token = jwt.encode({'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'])
            return jsonify({'status': True, 'token': token.decode('UTF-8'), 'msg': "User created successfuly!!"})
    except:
        return jsonify({'status': False, 'msg': 'Please enter the requiered values!'}), 400

@app.route('/products/add', methods=['POST'])
@token_required
def add_product():
    try:
        token = request.headers.get('Authorization').split("Bearer ")[1]
        user = jwt.decode(token, app.config['SECRET_KEY'])['user']
        title = request.json['title']
        description = request.json['description']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO products(title, description, user) VALUES(%s, %s, %s)", (title, description, user))
        mysql.connection.commit()
        cur.close()
        return jsonify({'status': True, 'msg': 'Product added successfuly!'})
    except:
        return jsonify({'status': False, 'msg': 'Please enter the required values!'}), 400

@app.route('/products')
def get_products():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    return jsonify(products)

@app.route('/email')
def email():
    try:
        msg = MIMEMultipart()
        message = "Hello faggot!"
        password = 'drugs4nerdz69'
        msg['From'] = 'dr4nerdz69@gmail.com'
        msg['To'] = 'redis123445@gmail.com'
        msg['Subject'] = 'SUCK IT'
        msg.attach(MIMEText(message, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com: 587')
        server.starttls()
        server.login(msg['From'], password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        return 'Email Sent'
    except:
        return 'Error!', 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')