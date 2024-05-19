from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from urllib.parse import urlparse
from funciones import calcular_edad, parsear_fecha, ver_atributos
from database import create_connection
from datetime import datetime
from models import User
from forms import SignUpForm, LoginForm, RegistroForm
from flask_wtf import CSRFProtect
import config
import pyodbc

from werkzeug.datastructures import MultiDict


app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config["SESSION_PERMANENT"] = config.SESSION_PERMANENT
app.config["SESSION_TYPE"] = config.SESSION_TYPE

#csrf = CSRFProtect(app)
# inicializar el LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
# las rutas con @login_required redirigen a '/login' si no inició sesión
login_manager.login_view = 'login'

@app.route('/index')
def index():
    return render_template('index.html', user = current_user)

@app.route('/')
def Inicio():
    return render_template('Inicio.html',user = current_user)

@app.route('/alumno')
@login_required
def mostrar_formulario():
    return render_template('formulario_agregar_alumno.html', user=current_user)

@app.errorhandler(404)
def page_not_found(e):
    # Si no existe la pagina vuelve al INICIO
    return redirect(url_for('index'))
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
            app.logger.info('Alumno eliminado con éxito')
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

            cursor.execute("SELECT ID_anio FROM Anios_nacimiento WHERE Anio = ?", (anio,))
            result_anio = cursor.fetchone()
            if result_anio:
                id_anio = result_anio[0]
            else:
                cursor.execute("INSERT INTO Anios_nacimiento (Anio) VALUES (?)", (anio,))
                conn.commit()
                id_anio = cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]

            cursor.execute("SELECT ID_mes FROM Meses_nacimiento WHERE Mes = ?", (mes,))
            result_mes = cursor.fetchone()
            if result_mes:
                id_mes = result_mes[0]
            else:
                cursor.execute("INSERT INTO Meses_nacimiento (Mes) VALUES (?)", (mes,))
                conn.commit()
                id_mes = cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]

            cursor.execute("SELECT ID_dia FROM Dias_nacimiento WHERE Dia = ?", (dia,))
            result_dia = cursor.fetchone()
            if result_dia:
                id_dia = result_dia[0]
            else:
                cursor.execute("INSERT INTO Dias_nacimiento (Dia) VALUES (?)", (dia,))
                conn.commit()
                id_dia = cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]

            cursor.execute("UPDATE Alumnos SET Nombres = ?, Ap_pat = ?, Ap_mat = ?, Edad = ?, Total_asistencias = ?, ID_anio_nac = ?, ID_mes_nac = ?, ID_dia_nac = ? WHERE ID_alumno = ?", 
                           (nombre, apellido_paterno, apellido_materno, edad, total_asistencia, id_anio, id_mes, id_dia, alumno_id))
            conn.commit()
            return redirect(url_for('mostrar_todos_los_alumnos')) 
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
    # llama al método estático en el modelo
    return User.get_user(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # si ya inició sesión, hay que redigirirlo al index
    if current_user.is_authenticated:
        return redirect(url_for('Inicio')) 

    # creamos el formulario de login
    form = LoginForm()

    if request.method == 'GET':
        return render_template('login.html', message = None, form = form)
    
    if request.method == 'POST':
        if form.validate_on_submit():
            app.logger.info('[Formulario] - Login validado')
            # recuperamos información del formulario
            user = form.username.data
            pswd = form.password.data

            conn = create_connection()
            if conn is not None:
                try:
                    # buscamos en la base de datos el usuario
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM Users WHERE Username = ?", (user,))
                    user = cursor.fetchone()
                    if user is not None:
                        # si el usuario existe, lo convertimos al modelo Useer
                        user_model = User(user.Username, user.Password, user.Email, False)
                        # checamos si la contraseña ingresada coincide (se comparan hashes)
                        if user_model.check_password(pswd):
                            # con esta función, Flask-Login reconoce que hemos iniciado sesión
                            login_user(user_model)
                            app.logger.info(f'Inicio se sesión exitoso: {user_model.id}') 
                            # en el form debe haber <input type="hidden" name="next" value="{{ request.args.get('next', '') }}" />
                            # si el usuario ingresa a una página no autorizada, se le redirige al login y al iniciar sesión,
                            # entonces lo mandamos a donde quería ingresar:
                            next = request.form.get('next')
                            if not next or urlparse(next).netloc != '':
                                # lo redirigimos al index
                                next = url_for('index')
                            return redirect(next) 
                        
                        # si la contraseña es incorrecta, mostrar error
                        return render_template('login.html', message = { 'text': 'Contraseña incorrecta'}, form=form)
                    # si user is None, mostrar usuario no encontrado
                    return render_template('login.html', message = { 'text': 'Usuario no encontrado'}, form=form)   
                except pyodbc.Error as e:
                    print(f"Error manipular la base de datos: {str(e)}")
                finally:
                    conn.close()
                    
        else: # Si el formulario no fue validado por algún motivo
            app.logger.info('[Formulario] - [ERROR] - Formulario no validado:')
            if form.username.errors:
                app.logger.info(f'[Formulario] - [Field] - [Username]')
                for error in form.username.errors:
                    app.logger.info(f'[Formulario] - [Error-info] - {error}')
            if form.password.errors:
                app.logger.info(f'[Formulario] - [ERROR] - [Password]')
                for error in form.password.errors:
                    app.logger.info(f'[Formulario] - [Error-info] - {error}')
            return render_template('login.html', message=None, form=form)
            

        # si la conexión falló o hubo una excepción, mostrar error
        return render_template('login.html', message = { 'text': 'Hubo un error relacionado con la base de datos.'}, form=form)
    pass

@app.route('/registro', methods=['GET', 'POST'])
def registro():
     # si ya inició sesión, hay que redigirirlo al index
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # crear el modelo de formulario
    form = RegistroForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            nombres = form.nombres.data
            apellido_p = form.apellido_paterno.data
            apellido_m = form.apellido_materno.data
            username = form.username.data
            email = form.email.data
            password = form.password.data
            confirmar_password = form.confirm_password.data

            print(f'{password} != {confirmar_password}')
            if password != confirmar_password:
                flash('Las contraseñas no coinciden, asegúrate de volver a escribirla correctamente.', 'error')
                msg = { 'text':'Las contraseñas no coinciden. Asegúrate de confirmar tu contraseña correctamente.' }
                return render_template('register.html', message = msg, form=form) 
            
            conn = create_connection()
            if conn is not None:
                try:
                    cursor = conn.cursor()
                    existent_user = User.get_user(username)
                    if existent_user is not None:
                        app.logger.warning('Ya existe un usuario con este username. Registro inválido')
                        msg = { 'text':'El nombre de usuario ya existe.' }
                        return render_template('register.html', message = msg, form = form) 
                    else:
                        query_insert = 'INSERT INTO Users (Username, Password, Email, Nombres, Ap_pat, Ap_mat, Fecha_creacion)\
                                        VALUES (?, ?, ?, ?, ?, ?, GETDATE())'
                        params = (username, password, email, nombres, apellido_p, apellido_m,)
                        cursor.execute(query_insert, params)
                        cursor.commit()
                        app.logger.warning(f'[REGISTRO => {datetime.now()}] Registro completado con éxito: username - {username}')
                        # flash() guarda un mensaje que sólo será visto en la siguiente solicitud y se elimina
                        flash('Registro completado con éxito') 
                        return redirect(url_for('login'))
                    
                except pyodbc.Error as e:
                    print(f"Error manipular la base de datos: {str(e)}")
                finally:
                    conn.close()
        else:
            app.logger.info('[Formulario] - [ERROR] - Formulario no validado:')
            for field in form.errors:
                app.logger.info(f'[Formulario] - [Field] - [{field}]')
                for error in getattr(form, f'{field}').errors:
                    app.logger.info(f'[Formulario] - [Field] - [{field}] - [{error}]')
    return render_template('register.html', form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return(redirect(url_for('Inicio')))

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
                    INNER JOIN Estatus ON Alumnos.ID_estatus = Estatus.ID_estatus \
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

    # hay 2 botones name=submit, dependiendo del value en el html se hace una cosa u otra
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
    app.logger.warning('Ocurrió un imprevisto')
    return redirect(url_for('index'))


"""
NADA DE LO QUE HAY DESPUÉS DE 
ESTO TIENE UNA FUNCIÓN REAL
"""
# ----------- ruta para testear funciones nuevas ---------------------
@app.route('/test', methods = ['GET', 'POST'])
def tests():
    # aqui va código que quieras testear
    # nuevas funcionalidades o cosas así

    registro = RegistroForm()
    registro.confirm_password.process_data('s ')
    if registro.confirm_password.validate('_'):
        print('Valido')
    else:
        print(f'No válido: {registro.confirm_password.errors}')

    if request.method == 'POST':
        print(type(request.form))

    form = SignUpForm()
    print(form.date_min)
    print(form.date_max)
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        telefono = form.telefono.data
        email = form.email.data
        date = form.date.data

        app.logger.info('Formulario de registro validado:'
                        f'\n\t\tUsername: {username}\n\t\tPassword: {password}\n\t\tEmail: {email}\n\t\tTeléfono: {telefono}\n\t\tDate: {date}')
    else:
        print(f'Errores en el form:\n{form.errors}')

    return render_template('form_test.html', form = form)
    #return render_template('test.html')
# ---------------------------------------------------------------------

@app.route('/consulta')
def consulta():
    conn = create_connection()
    if conn is not None:
        try:
            query = "SELECT * FROM Alumnos \
                    INNER JOIN Meses_nacimiento ON Alumnos.ID_mes_nac = Meses_nacimiento.ID_mes \
                    INNER JOIN Anios_nacimiento ON Alumnos.ID_anio_nac = Anios_nacimiento.ID_anio \
                    INNER JOIN Dias_nacimiento ON Alumnos.ID_dia_nac = Dias_nacimiento.ID_dia \
                    INNER JOIN Cintas ON Alumnos.ID_cinta = Cintas.ID_cinta \
                    INNER JOIN Telefonos ON Alumnos.ID_alumno = Telefonos.ID_telefono \
                    INNER JOIN Estatus ON Alumnos.ID_estatus = Estatus.ID_estatus \
                    WHERE ID_alumno = ?"

            cursor = conn.cursor()
            cursor.execute(query, (id))
            alumno = cursor.fetchone()
            if alumno is not None:
                return render_template('perfil.html', user = current_user, alumno = alumno)
            return f'No hay un alumno con el id {id} en la base de datos.'

        except pyodbc.Error as e:
            app.logger.error(f"[ERROR EN EL PROGRAMA] Error al ejecutar la consulta: {str(e)}")
            print( 'Error al recuperar la información del alumno.')
        finally:
            conn.close()
    else:
        pass

    return render_template('testeando_fechas.html')

@app.route('/api/horarios/<id_dia>', methods = ['GET'])
def recuperar_horario(id_dia):
    print('inicio')
    conn = create_connection()
    if conn is not None:
        try:
            print('try')
            query = "SELECT Dias_semana.Dia, Dias_semana.ID_dia_sem, Horarios.Hora FROM Clases \
                    INNER JOIN Dias_semana ON Clases.ID_dia_semana = Dias_semana.ID_dia_sem \
                    INNER JOIN Horarios ON Clases.ID_hora = Horarios.ID_hora \
                    WHERE UPPER(Dias_semana.ID_dia_sem) = ?"
            params = (id_dia,)
            cursor = conn.cursor()
            cursor.execute(query, params)
            clases = cursor.fetchall()
            if clases is not None:

                resultados = []
                for clase in clases:
                    print(f'dia: {clase[0]}, id_dia: {clase[1]}, hora: {clase[2]}')
                    resultados.append({ 'dia':f'{clase[0]}', 'id_dia':f'{clase[1]}', 'hora':f'{clase[2]}'})

                print(resultados)
                json = jsonify(resultados)
                return json
            
            print('No se encontraron clases para el viernes (???)')
            return 'None'

        except pyodbc.Error as e:
            app.logger.error(f"[ERROR EN EL PROGRAMA] Error al ejecutar la consulta: {str(e)}")
            print( 'Error al recuperar la información del alumno.')
        finally: conn.close()

    return 'None'
    

@app.route('/request/validation/signup', methods = ['GET'])
def getFormErrors():
    data = {
        'nombre': 'XD'
    }
    json = jsonify(data)
    print(json)
    return json
 
if __name__ == '__main__':
    app.run(debug=True)
