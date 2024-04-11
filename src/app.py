from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from datetime import datetime
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


@app.route('/register', methods = ['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':

        nombre = request.form['name-1']
        apellP = request.form['name-2']
        apellM = request.form['name-3']
        email = request.form['email']
        fecha = request.form.get('fecha')
        username = request.form['username']
        pswd = request.form['password']

        print(f'Datos a registrar: {(nombre, apellP, apellM, email, fecha, username, pswd)}')
        # Buscar en la BD si ya existe el usuario o el correo
        cur = mysql.connection.cursor()
        cur.execute('select * from users where username = %s or email = %s', (username, email))
        existingUser = cur.fetchone()

        # Si el usuario o correo no existen en la BD insertar
        if existingUser is None:
            cur.execute('insert into users(nombre, apellido_paterno, apellido_materno, email, fecha_nacimiento, password, username) values(%s, %s, %s, %s, %s, %s, %s)',
                        (nombre, apellP, apellM, email, fecha, pswd, username))
            mysql.connection.commit()
            print("Registro exitoso")
            cur.close()
            # Redireccionar al login con mensaje de éxito
            return redirect(url_for('home'), mensaje="registro")
        else:
            print(f'Ya existe un usuario registrado con ese correo y/o usuario: {(email, username)}')
            cur.close()
            # Regresar con un error
            return render_template('register.html', mensaje="error")
            
@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    # Si request.methos es 'POST'
    userEmail = request.form['user']
    password = request.form['password']
    cur = mysql.connection.cursor()
    cur.execute('select * from users where username = %s or email = %s', (userEmail, userEmail))
    user = cur.fetchone()
    cur.close()
    # Si se encontró el correo o usuario
    if user is not None:
        # Ahora ver si la contraseña es correcta
        if user[6] == password:
            print(f'La contraseña coincide: {user[6]} | {password} | username: {user[7]}')
            session['id'] = user[0]
            session['nombre'] = user[1]
            session['apellido_paterno'] = user[2]
            session['apellido_materno'] = user[3]
            session['fecha_nacimiento'] = user[4].strftime('%Y-%m-%d' )
            session['email'] = user[5]
            session['username'] = user[7]

            # redirigir a la página principal
            return redirect(url_for('biblioteca', username = user[7]))
        else:
            print(f'Contraseña incorrecta: {user[6]} | {password}')
            return render_template('login.html', mensaje = "incorrecto")

    else:
        print(f'No se encontró {(userEmail, password)} en la base de datos')
        return render_template('login.html', mensaje = "no existe")


# SELECT
@app.route('/<username>/biblioteca', methods = ['GET'])
def biblioteca(username):
    cur = mysql.connection.cursor()
    cur.execute('select * from users where username = %s', (username,))
    user = cur.fetchone()
    if user is not None:
        cur.execute('select * from libros where usuario = %s', (username,))
        libros = cur.fetchall()
        cur.close()
        return render_template('biblioteca.html', user = user, libros = libros)
    
    cur.close()
    return redirect(url_for('home'))


# INSERT
@app.route('/add-libro', methods = ['POST'])
def addLibro():
    fecha = datetime.now().strftime('%Y-%m-%d')
    titulo = request.form['titulo']
    autor = request.form['autor']
    editorial = request.form['editorial']
    edicion = request.form['edicion']
    genero = request.form['genero']
    year = request.form['año']
    username = request.form['username']
    portada  = request.form['portada']

    cur = mysql.connection.cursor()
    cur.execute('insert into libros (titulo, autor, genero, edicion, editorial, anio_publicacion, fecha_modificacion, usuario, portada) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                (titulo, autor, genero, edicion, editorial, year, fecha, username, portada))
    
    mysql.connection.commit()

    cur.close()
    return redirect(url_for('biblioteca', username = username))
    

# UPDATE
@app.route('/edit-libro/<int:id>', methods=['POST'])
def editLibro(id):
    titulo = request.form['titulo']
    autor = request.form['autor']
    editorial = request.form['editorial']
    edicion = request.form['edicion']
    genero = request.form['genero']
    year = request.form['año']
    username = request.form['username']
    portada = request.form['portada']

    cur = mysql.connection.cursor()
    cur.execute('update libros set titulo = %s, autor = %s, genero = %s, edicion = %s, editorial = %s, anio_publicacion = %s, portada = %s where id = %s', 
                (titulo, autor, genero, edicion, editorial, year, portada, id))
    cur.connection.commit();
    cur.close();

    return redirect(url_for('biblioteca', username = username))

# DELETE
@app.route('/delete-libro', methods=['POST'])
def deleteLibro():
    id = request.form['libro_id']
    username = request.form['libro_username']

    cur = mysql.connection.cursor()
    cur.execute('delete from libros where id = %s', (id))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('biblioteca', username = username))

if __name__ == '__main__':
    app.run(debug=True)

