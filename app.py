from flask import Flask, Response, jsonify, request
from flask_mysqldb import MySQL
import jwt
import datetime
from secret import mysql_password, secret_key
from functools import wraps

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
    return jsonify({'status': True, 'msg': 'Token is valid!'})

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')