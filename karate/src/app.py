from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from models import User
from funciones import calcular_edad, parsear_fecha
from database import create_connection
import config
import pyodbc


app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config["SESSION_PERMANENT"] = config.SESSION_PERMANENT
app.config["SESSION_TYPE"] = config.SESSION_TYPE

# inicializar el LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
# las rutas con @login_required redirigen a '/login' si no inició sesión
login_manager.login_view = 'login'

#Direcciones---------------------------------------
@app.route('/')
def index():
    return render_template('index.html', user = current_user)

@app.route('/alumno')
@login_required
def mostrar_formulario():
    return render_template('formulario_agregar_alumno.html')

#--------------------------------------------------

# METODOS PARA AGREGAR ALUMNOS ------------------------------------------------------------------
@app.route('/agregar_alumno', methods=['POST'])
@login_required
def agregar_alumno():
    nombre = request.form.get('nombres')
    apellido_paterno = request.form.get('ap_pat')
    apellido_materno = request.form.get('ap_mat')

    # Se debe parsear la fecha como proviene del formulario al de la BD
    fecha = request.form['fecha_nacimiento']
    fecha_nacimiento = parsear_fecha(fecha)
    dia = fecha_nacimiento.day
    mes = fecha_nacimiento.month
    anio = fecha_nacimiento.year

    # edad se calcula con la fecha
    edad = calcular_edad(fecha_nacimiento)

    total_asistencias = 0
    telefono = request.form.get('telefono')

    id_anio = 0
    id_mes = mes
    id_dia = 0
    id_cinta = int(request.form.get('id_cinta'))

    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            #telefono_existe = cursor.execute('SELECT Telefono FROM Telefonos WHERE = (?)', ())
            cursor.execute('INSERT INTO Telefonos (Telefono) VALUES (?)', (telefono,))
            conn.commit()
            print('Teléfono del alumno agregado con éxito...')

            cursor.execute("SELECT ID_anio FROM Anios_nacimiento WHERE Anio = ?", (anio,))
            result_anio = cursor.fetchone()
            if result_anio:
                id_anio = result_anio[0]
            else:
                cursor.execute("INSERT INTO Anios_nacimiento (Anio) VALUES (?)", (anio,))
                conn.commit()
                id_anio = cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]

            cursor.execute("SELECT ID_dia FROM Dias_nacimiento WHERE Dia = ?", (dia,))
            result_dia = cursor.fetchone()
            if result_dia:
                id_dia = result_dia[0]
            else:
                cursor.execute("INSERT INTO Dias_nacimiento (Dia) VALUES (?)", (dia,))
                conn.commit()
                id_dia = cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]

            insertQuery = "INSERT INTO Alumnos \
                (Nombres, Ap_pat, Ap_mat, Edad, Total_asistencias, \
                ID_anio_nac, ID_mes_nac, ID_dia_nac, ID_cinta) \
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            params = (nombre, apellido_paterno, apellido_materno, edad, total_asistencias, id_anio, id_mes, id_dia, id_cinta)
            
            cursor.execute(insertQuery,params)
            conn.commit()

            return redirect(url_for('mostrar_todos_los_alumnos'))
        
        except pyodbc.Error as e:
            print(f"Error al insertar alumno en la base de datos: {str(e)}")
            return 'Error al agregar alumno'
        finally:
            conn.close()
    else:
        return 'Error al conectar a la base de datos'

#-------------------------------------------------------------------------------------------------------

# METODO PARA MOSTRAR ALUMNOS----------------------------------------------------------------------------
@app.route('/alumnos/lista')
@login_required
def mostrar_todos_los_alumnos():
    # Conectar a la base de datos
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            # Obtener todos los alumnos de la base de datos
            query = "SELECT * FROM Alumnos \
                    INNER JOIN Meses_nacimiento ON Alumnos.ID_mes_nac = Meses_nacimiento.ID_mes \
                    INNER JOIN Anios_nacimiento ON Alumnos.ID_anio_nac = Anios_nacimiento.ID_anio \
                    INNER JOIN Cintas ON Alumnos.ID_cinta = Cintas.ID_cinta \
                    INNER JOIN Telefonos ON Alumnos.ID_alumno = Telefonos.ID_telefono"
            cursor.execute(query)
            alumnos = cursor.fetchall()

            query = "SELECT * FROM Cintas"
            cursor.execute(query)
            cintas = cursor.fetchall()

            return render_template('Tabla_Alumnos.html', user = current_user, alumnos = alumnos, cintas = cintas)
        except pyodbc.Error as e:
            print(f"Error al obtener todos los alumnos: {str(e)}")
            return F'Error al obtener los alumnos: {str(e)}'
        finally:
            conn.close()
    else:
        return 'Error al conectar a la base de datos'
#--------------------------------------------------------------------------------------------------------

# Método para eliminar un alumno por su ID ---------------------------------------------------------------
@app.route('/eliminar_alumno/<int:id>', methods=['POST'])
@login_required
def eliminar_alumno(id):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Alumnos WHERE ID_alumno = ?", (id,))
            conn.commit()
            app.logger.info('Alumno agregado con éxito')
        except pyodbc.Error as e:
            app.logger.error(f"Error al eliminar alumno de la base de datos: {str(e)}")
        finally:
            conn.close()
    else:
        app.logger.error('Error al conectar a la base de datos')

    return redirect(url_for('mostrar_todos_los_alumnos'))
 #--------------------------------------------------------------------------------------------------------

# METODO PARA ACTUALIZAR USUARIO-------------------------------------------------------------------------
@app.route('/editar_alumno', methods=['POST'])
@login_required
def editar_alumno():
    alumno_id = request.form['alumno_id']
    nombre = request.form['nombre']
    apellido_paterno = request.form['apellido_paterno']
    apellido_materno = request.form['apellido_materno']
    edad = request.form['edad']
    total_asistencia = request.form['total_asistencia']
    anio = request.form['anio']  
    mes = request.form['mes']
    dia = request.form['dia']

    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            cursor.execute("SELECT Id_Anio FROM Anio WHERE Anio = ?", (anio,))
            result_anio = cursor.fetchone()
            if result_anio:
                id_anio = result_anio[0]
            else:
                cursor.execute("INSERT INTO Anio (Anio) VALUES (?)", (anio,))
                conn.commit()
                id_anio = cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]

            cursor.execute("SELECT Id_Mes FROM Mes WHERE Mes = ?", (mes,))
            result_mes = cursor.fetchone()
            if result_mes:
                id_mes = result_mes[0]
            else:
                cursor.execute("INSERT INTO Mes (Mes) VALUES (?)", (mes,))
                conn.commit()
                id_mes = cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]

            cursor.execute("SELECT Id_Dias FROM Dias WHERE Dias = ?", (dia,))
            result_dia = cursor.fetchone()
            if result_dia:
                id_dia = result_dia[0]
            else:
                cursor.execute("INSERT INTO Dias (Dias) VALUES (?)", (dia,))
                conn.commit()
                id_dia = cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]

            cursor.execute("UPDATE Alumno SET Nombre = ?, Apellido_Paterno = ?, Apellido_Materno = ?, Edad = ?, Total_Asistencia = ?, Id_Anio = ?, Id_Mes = ?, Id_Dias = ? WHERE Id_Alumno = ?", 
                           (nombre, apellido_paterno, apellido_materno, edad, total_asistencia, id_anio, id_mes, id_dia, alumno_id))
            conn.commit()
            return redirect('/Tabla_Alumnos') 
        except pyodbc.Error as e:
            print(f"Error al actualizar alumno en la base de datos: {str(e)}")
            return 'Error al actualizar alumno'
        finally:
            conn.close()
    else:
        return 'Error al conectar a la base de datos'

# ----------- RUTAS REFERENTES AL LOGIN ---------------------------
@login_manager.user_loader
def load_user(user_id : str):
    # cada vez que el usuario loggeado entra a una página
    # LoginManager busca el ID del usuario en la BD para
    # acceder a sus datos
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE username = ?', (user_id,))

    user = cursor.fetchone()
    if user is not None:
        # si se encuentra el usuario entonces lo convertimos en un objeto del modelo
        user_model = User(user.username, user.password, user.email, False)
        # poner los setters
        user_model.set_nombres(user.nombres)
        user_model.set_apellido_paterno(user.ap_pat)
        user_model.set_apellido_materno(user.ap_mat)
        user_model.set_fecha_creacion(user.fecha_creacion)
        return user_model

    # si no encuentra nada, devolver None
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    # si ya inició sesión, hay que redigirirlo al index
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'GET':
        return render_template('login.html', message = None)

    if request.method == 'POST':
        # recuperamos información del formulario
        user = request.form.get('user')
        pswd = request.form.get('password')

        conn = create_connection()
        if conn is not None:
            try:
                # buscamos en la base de datos el usuario
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Users WHERE username = ?", (user,))
                user = cursor.fetchone()
                if user is not None:
                    # si el usuario existe, lo convertimos al modelo Useer
                    user_model = User(user.username, user.password, user.email, False)
                    # checamos si la contraseña ingresada coincide (se comparan hashes)
                    if user_model.check_password(pswd):
                        # con esta función, Flask-Login reconoce que hemos iniciado sesión
                        login_user(user_model)

                        app.logger.info(f'Inicio se sesión exitoso: {user_model.id}') 
                        # lo redirigimos al index
                        return redirect(url_for('index')) 
                    # si la contraseña es incorrecta, mostrar error
                    return render_template('login.html', message = { 'text': 'Contraseña incorrecta'})
                # si user is None, mostrar usuario no encontrado
                return render_template('login.html', message = { 'text': 'Usuario no encontrado'})   
            except pyodbc.Error as e:
                print(f"Error manipular la base de datos: {str(e)}")
            finally:
                conn.close()
        # si la conexión falló o hubo una excepción, mostrar error
        return render_template('login.html', message = { 'text': 'Hubo un error relacionado con la base de datos.'})

@app.route('/logout')
def logout():
    logout_user()
    return(redirect(url_for('index')))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
     # si ya inició sesión, hay que redigirirlo al index
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('register.html')


#-----------------PERFILES DE ALUMNOS ---------------------------
@app.route('/perfil/alumno/<int:id>', methods = ['GET'])
@login_required
def profile(id : int):
    conn = create_connection()
    if conn is not None:
        try:

            query = "SELECT * FROM Alumnos \
                    INNER JOIN Meses_nacimiento ON Alumnos.ID_mes_nac = Meses_nacimiento.ID_mes \
                    INNER JOIN Anios_nacimiento ON Alumnos.ID_anio_nac = Anios_nacimiento.ID_anio \
                    INNER JOIN Dias_nacimiento ON Alumnos.ID_dia_nac = Dias_nacimiento.ID_dia \
                    INNER JOIN Cintas ON Alumnos.ID_cinta = Cintas.ID_cinta \
                    INNER JOIN Telefonos ON Alumnos.ID_alumno = Telefonos.ID_telefono \
                    WHERE ID_alumno = ?"

            cursor = conn.cursor()
            cursor.execute(query, (id))
            alumno = cursor.fetchone()
            if alumno is not None:
                return render_template('perfil.html', user = current_user, alumno = alumno)
            
            return f'No hay un alumno con el id {id} en la base de datos.'

        except pyodbc.Error as e:
            app.logger.error(f"[ERROR EN EL PROGRAMA] Error al ejecutar la consulta: {str(e)}")
            return 'Error al recuperar la información del alumno.'
        finally:
            conn.close()
    else:
        return 'Error al conectar a la base de datos'

# ----------- CONSULTA DE PAGOS ATRASADOS --------------
@app.route('/consultas/pagos/<mes>/<anio>', methods = ['GET', 'POST'])
@login_required
def pagos_mes_anio(mes, anio):
    conn = create_connection()
    if conn is not None:
        try:
            query = 'SELECT Alumnos.Nombres, Alumnos.Ap_pat, Alumnos.Ap_mat, Telefonos.Telefono \
                FROM Alumnos, Telefonos, Pago_alumno, Historial_adeudos, Meses_adeudo, Anios_adeudo \
                WHERE Meses_adeudo.Mes = ? AND Anios_adeudo.Anio = ? \
                    AND Alumnos.ID_alumno = Telefonos.ID_telefono \
                    AND Alumnos.ID_alumno = Pago_alumno.ID_alumno \
                    AND Historial_adeudos.ID_pago_alumnos = Pago_alumno.ID_pago_alumno \
                    AND Historial_adeudos.ID_mes = Meses_adeudo.ID_mes \
                    AND Historial_adeudos.ID_anio = Anios_adeudo.ID_anio'
            params = (mes, anio)    

            cursor = conn.cursor()
            cursor.execute(query, params)
            alumnos = cursor.fetchall()

            id_mes = cursor.execute('SELECT ID_mes FROM Meses_adeudo WHERE Mes = ?', (mes,)).fetchone()[0]

            if alumnos is not None:
                app.logger.debug(f'Consulta realizada: {alumnos}')
                return render_template('pagos.html', user = current_user, alumnos = alumnos, mes = mes, ID_mes = id_mes, anio = anio)

        except pyodbc.Error as e:
            app.logger.error(f"[ERROR EN EL PROGRAMA] Error al ejecutar la consulta: {str(e)}")
        finally:
            conn.close()

        return 'Error al recuperar la información del alumno.'
    else:
        return 'Error al conectar a la base de datos'

@app.route('/consultas/pagos/todos', methods = ['GET'])
@login_required
def pagos_mes_anio_todos():
    conn = create_connection()
    if conn is not None:
        try:
            query = 'SELECT Alumnos.Nombres, Alumnos.Ap_pat, Alumnos.Ap_mat, Telefonos.Telefono, Meses_adeudo.Mes, Anios_adeudo.Anio \
                FROM Alumnos, Telefonos, Pago_alumno, Historial_adeudos, Meses_adeudo, Anios_adeudo \
                WHERE Alumnos.ID_alumno = Telefonos.ID_telefono \
                    AND Alumnos.ID_alumno = Pago_alumno.ID_alumno \
                    AND Historial_adeudos.ID_pago_alumnos = Pago_alumno.ID_pago_alumno \
                    AND Historial_adeudos.ID_mes = Meses_adeudo.ID_mes \
                    AND Historial_adeudos.ID_anio = Anios_adeudo.ID_anio'
            cursor = conn.cursor()
            cursor.execute(query)
            alumnos = cursor.fetchall()

            if alumnos is not None:
                app.logger.debug(f'Consulta realizada: {alumnos}')
                return render_template('pagos_completos.html',user = current_user, alumnos = alumnos)

        except pyodbc.Error as e:
            app.logger.error(f"[ERROR EN EL PROGRAMA] Error al ejecutar la consulta: {str(e)}")
        finally:
            conn.close()

        return 'Error al recuperar la información del alumno.'
    else:
        return 'Error al conectar a la base de datos'

@app.route('/consultas/pagos/recuperar', methods=['POST'])
@login_required
def procesar_consulta_pagos():
    # hay 2 botones submit, dependiendo del value en el html se hace una cosa u otra
    if request.form.get('submit') == 'Mostrar todos los registros':
        return redirect('/consultas/pagos/todos')

    elif request.form.get('submit') == 'Actualizar consulta':
        # se obtiene la fecha que se puso (en string)
        consulta = request.form.get('fecha')
        # se convierte el string en un objeto datetime para sacar el mes y el año
        fecha = parsear_fecha(f'{consulta}-01')

        conn = create_connection()
        cursor = conn.cursor()
        mes = cursor.execute('SELECT Mes FROM Meses_nacimiento WHERE ID_mes = ?', (fecha.month,)).fetchone()[0]
        anio = fecha.year
        cursor.close()

        # se envía la información a la página
        return redirect(f'/consultas/pagos/{mes}/{anio}')
    
    # por si ocurre algún imprevisto, refresa al index
    return redirect(url_for('index'))


# ----------- ruta para testear funciones nuevas ---------------------
@app.route('/test')
def tests():
    # aqui va código que quieras testear
    # nuevas funcionalidades o cosas así
    return render_template('test.html')
# ---------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
