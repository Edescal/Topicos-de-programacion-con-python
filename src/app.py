from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import config

app = Flask(__name__)
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
app.config['SECRET_KEY'] = config.HEX_SEC_KEY

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods = ['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    cur = mysql.connection.cursor()
    cur.execute('select * from users where email = %s and password = %s', (email, password))
    user = cur.fetchone()
    cur.close()
    if user is not None:
        session['email'] = email
        session['name'] = user[1]
        session['surnames'] = user[2]
        print(f'Sí se encontró en la base de datos: {user}')
        return redirect(url_for('success'))
    else:
        return render_template('login.html', message = '¡Correo o contraseña incorrectos!')

@app.route('/success')
def success():
    return render_template('success.html')

app.run(debug=True)
