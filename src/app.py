from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import config

app = Flask(__name__)
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
app.config['HEX_SEC_KEY'] = config.HEX_SEC_KEY

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
    info = cur.fetchone()
    cur.close()

    if info == None:
        print('No se encontró en la base de datos')
        return render_template('login.html', message = '¡Correo o contraseña incorrectos!')
    else:
        print(f'Sí se encontró en la base de datos: {info}')
        return redirect(url_for('success'))

@app.route('/success')
def success():
    return render_template('success.html')

app.run(debug=True)
