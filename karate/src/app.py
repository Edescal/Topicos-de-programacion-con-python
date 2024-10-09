from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, send_from_directory
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from urllib.parse import urlparse
from funciones import calcular_edad, parsear_fecha, ver_atributos, capitalize_each, fetch_all_to_dict_list, nums_to_str_date, diferencia_meses, nombre_mes
from database import create_connection
from datetime import datetime
from dateutil.relativedelta import relativedelta
from models import User, Alumno
from forms import LoginForm, RegistroForm, AlumnoForm, EditarAlumnoForm, ValidarPagoForm, RegistrarAsistenciaForm, SignUpForm
from flask_wtf import CSRFProtect
import config
import pyodbc
import mariadb


app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config["SESSION_PERMANENT"] = config.SESSION_PERMANENT
app.config["SESSION_TYPE"] = config.SESSION_TYPE
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


#csrf = CSRFProtect(app)
# inicializar el LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
# las rutas con @login_required redirigen a '/login' si no inició sesión
login_manager.login_view = 'login'
login_manager.login_message = "Inicia sesión para visualizar esta página."


@app.route('/')
@app.route('/index')
def index():
    # nombres = 'Narcisso'
    # apellido_p = 'Anasui'
    # apellido_m = 'Brando'
    # username = 'admin'
    # email = 'admin@senshi.karate.com'
    # password = generate_password_hash('password')
    # fecha = '2000-08-15'

    # config = {
    #         'host': '127.0.0.1',
    #         'port': 3307,
    #         'user': 'root',
    #         'password': 'super',
    #         'database': 'karate'
    #     }
    # conn = mariadb.connect(**config)
    # cur = conn.cursor()

    # query = """
    # insert into users (username, password, email, nombres, apellido_paterno, apellido_materno, fecha_creacion)
    # values (?,?,?,?,?,?,?)
    # """

    #print(len(password))
    #cur.execute(query, (username, password, email, nombres, apellido_p, apellido_m, fecha))
    #conn.commit()

    # cur.execute('select *    from users')
    # rows = cur.fetchall()
    # for result in rows:
    #     print(result)
    

    return render_template('index.html',user = current_user)

@app.errorhandler(404)
def page_not_found(e):
    app.logger.error(f'Error en el programa: {str(e)}')
    # Si no existe la pagina vuelve al INICIO
    return redirect(url_for('index'))

@app.route('/favicon.ico') 
def favicon(): 
    #return url_for('static', filename='data:,') # poner esto si no hay favicon.ico
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
#--------------------------------------------------


@app.route('/bajas', methods=['GET'])
def bajas():

    alumnos = Alumno.get_all(False, current_user=current_user)
    alumnos_baja = []
    if alumnos is not None:
        for alumno in alumnos:
            if alumno.estatus == 'BAJA':
                print(f'De baja: {alumno}')
                alumnos_baja.append(alumno)

    if len(alumnos_baja) == 0:
        flash('No hay alumnos para esta cuenta dados de baja', 'success')
    else:
        flash('Lista de alumnos que han sido dados de baja', 'success')

    return render_template('alumnos_baja.html',user = current_user, alumnos = alumnos_baja)
#-----------------METODO PARA REINCORPORAR ALUMNOS-------------------------------------

@app.route('/reincorporar/<int:id>', methods=['POST'])
def reincorporar_alumno(id):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE Alumnos SET ID_estatus = 1 \
                            WHERE Alumnos.ID_alumno = ?", (id,))
            conn.commit()
            flash("Se reincorporó al alumno con éxito")
            return redirect(url_for('bajas')) 
        except pyodbc.Error as e:
            print(f'Error: {str(e)}')
            flash("Error al reincorporar al alumno en la base de datos")
            return redirect(url_for('bajas')) 
        finally:
            conn.close()
    else:
        flash("Error al conectar la base de datos")
        return redirect(url_for('bajas')) 

"""
RUTAS PARA CONTROLAR LOS ALUMNOS
"""

@app.route('/agregar_alumno', methods=['POST'])
@login_required
def agregar_alumno():
    form = AlumnoForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            nombres = form.nombres.data
            apellido_paterno = form.apellido_paterno.data
            apellido_materno = form.apellido_materno.data
            telefono = form.telefono.data
            fecha_nacimiento = f'{form.fecha_nacimiento.data.year}-{form.fecha_nacimiento.data.month}-{form.fecha_nacimiento.data.day}'
            edad = calcular_edad(form.fecha_nacimiento.data)
            cinturon = form.cinturon.data
            estatus = 2
            conn = create_connection()
            if conn is not None:
                try:
                    cursor = conn.cursor()
                    consultar_telefono = 'select Numero from Telefonos where Numero = ?'
                    params = (telefono,)
                    cursor.execute(consultar_telefono, params)
                    telefono_exists = cursor.fetchone()
                    if telefono_exists is not None:
                        flash('El teléfono ya está registrado.', 'error')
                    else:
                        # primero se inserta el teléfono en la BD
                        insertar_telefono = 'insert into Telefonos (Numero) values (?)'
                        params = (telefono,)
                        cursor.execute(insertar_telefono, params)
                        # luego se inserta el alumno en la BD
                        insertar_alumno = 'insert into Alumnos (Nombres, Apellido_paterno, Apellido_materno, Edad, Fecha_nac, Asistencias, ID_cinta, ID_estatus, ID_user) values (?,?,?,?,?,?,?,?,?)'
                        params = (nombres, apellido_paterno, apellido_materno, edad, fecha_nacimiento, 0, cinturon, estatus, current_user.get_id())
                        print(f'Validado: {params}')
                        cursor.execute(insertar_alumno, params)
                        # luego se hace el commit
                        flash('El alumno fue registrado con éxito.', 'success') 
                        conn.commit()
                except mariadb.Error as e: 
                    print(f"Error al insertar alumno en la base de datos: {str(e)}")
                    flash('Hubo un error al registrar al nuevo alumno. Se revirtió la operación', 'error')
                    cursor.rollback()
                finally: conn.close()
            else: # conexión
                flash('Hubo un error al conectarse a la base de datos', 'error')
        else: # formulario
            flash('Los datos ingresados son inválidos. Vuelve a intentarlo', 'error') 
            print("Esta consulta no fue validada")
    #
    return redirect(url_for('mostrar_todos_los_alumnos'))

@app.route('/alumnos/lista')
@login_required
def mostrar_todos_los_alumnos():
    form = AlumnoForm()
    editForm = EditarAlumnoForm()
    alumnos = Alumno.get_all(True, current_user=current_user)
    print(alumnos)
    return render_template('Tabla_Alumnos.html', user = current_user, form = form, editForm = editForm, alumnos = alumnos)

# Método para eliminar un alumno por su ID ---------------------------------------------------------------
@app.route('/eliminar_alumno/<int:id>', methods=['POST'])
@login_required
def eliminar_alumno(id):
    alumno = Alumno.get_by_id(id, current_user=current_user)
    if alumno is not None:
        conn = create_connection()
        if conn is not None:
            try:
                consulta = 'UPDATE Alumnos SET ID_estatus = ? WHERE ID_alumno = ?'
                params = (3, id)
                cursor = conn.cursor()
                cursor.execute(consulta, params)
                conn.commit()
                app.logger.info('Se cambió el estatus del alumno con éxito')
                flash(f'Se cambió el estatus del alumno {alumno.nombres} {alumno.apellido_paterno} con éxito', 'success')
            except pyodbc.Error as e: 
                flash('No se pudo cambiar el estatus del alumno', 'error')
                app.logger.error(f"Error al cambiar el estatus del alumno en la base de datos: {str(e)}")
            finally: conn.close()
        else:
            flash('Error al procesar la información', 'error') 
            app.logger.error('Error al conectar a la base de datos')
    else:
        flash('El alumno que se intentó eliminar no existe o no tiene los permisos para modificarlo', 'error') 
        app.logger.error(f'El alumno que se intentó eliminar (ID = {id}) no existe o no tiene los permisos para modificarlo.')
    return redirect(url_for('mostrar_todos_los_alumnos'))
 #--------------------------------------------------------------------------------------------------------

# METODO PARA ACTUALIZAR USUARIO-------------------------------------------------------------------------
@app.route('/editar_alumno', methods=['POST'])
@login_required
def editar_alumno():
    form = EditarAlumnoForm()
    if form.validate_on_submit():
        id_alumno = form.id_alumno.data
        nombres = capitalize_each(form.nombres.data)
        apellido_paterno = capitalize_each(form.apellido_paterno.data)
        apellido_materno = capitalize_each(form.apellido_materno.data)
        telefono = form.telefono.data
        fecha_nacimiento = f'{form.fecha_nacimiento.data.year}-{form.fecha_nacimiento.data.month}-{form.fecha_nacimiento.data.day}'
        edad = calcular_edad(form.fecha_nacimiento.data)
        cinturon = form.cinturon.data
        estatus = form.estatus.data

        print(f'Form validado (1/3): {(id_alumno, nombres, apellido_paterno, apellido_materno, telefono, edad, 0, fecha_nacimiento, cinturon, estatus)}')
        
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute('select Count(Id_telefono) from Telefonos where Numero = ? AND ID_telefono != ?', (telefono, id_alumno,))
                telefono_exists = cursor.fetchone()
                print(telefono_exists)
                # asegurar que el nuevo telefono no es un duplicado de otro alumno
                es_propio = telefono_exists[0] == 0
                if telefono_exists is not None and not es_propio: 
                    flash('El teléfono ya está vinculado a otro alumno. No se actualizaron los datos.', 'error')
                else:
                    print(f'Telefono validado (2/3): {(id_alumno, nombres, apellido_paterno, apellido_materno, telefono, edad, 0, fecha_nacimiento, cinturon, estatus)}')

                    update_telefono = 'update Telefonos set Numero = ? where ID_telefono = ?' 
                    params = (telefono, id_alumno)
                    cursor.execute(update_telefono, params)

                    update_alumno = 'update Alumnos set Nombres = ?, apellido_paterno = ?, apellido_materno = ?, Edad = ?, fecha_nac = ?, ID_cinta = ?, ID_estatus = ? where ID_alumno = ?'
                    params = (nombres, apellido_paterno, apellido_materno, edad, fecha_nacimiento, cinturon, estatus, id_alumno)
                    cursor.execute(update_alumno, params)

                    print('Edición completada exitosamente (3/3)')
                    flash(f'Los datos del alumno se actualizaron con éxito.', 'success')
                    conn.commit()
            except pyodbc.Error as e: 
                print(f'Error: {str(e)}')
                conn.rollback()
            finally: conn.close()
    
    next = request.form.get('next')
    if not next or urlparse(next).netloc != '':
        # lo redirigimos al index
        next = url_for('mostrar_todos_los_alumnos')
    print(f'Redirect to {next}')
    return redirect(next) 

# ----------- Método para cambiar el estado del alumno --------------
@app.route('/cambiar_estado_alumno', methods=['POST'])
@login_required
def cambiar_estado_alumno():
    if request.method == 'POST':
        alumno_id = request.form.get('alumno_id')
        nuevo_estado = request.form.get('nuevo_estado')
        # Conectar a la base de datos
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                # Actualizar el estado del alumno en la base de datos
                update_query = "UPDATE Alumnos SET ID_estatus = ? WHERE ID_alumno = ?"
                cursor.execute(update_query, (nuevo_estado, alumno_id))
                conn.commit()
                flash("Estado del alumno actualizado con éxito.")
                return redirect(url_for('profile', id=alumno_id))  # Redirigir al perfil del estudiante actualizado
            except pyodbc.Error as e:
                flash(f"Error al actualizar el estado del alumno: {str(e)}")
                return redirect(url_for('profile', id=alumno_id))  # Redirigir al perfil del estudiante sin cambios
            finally:
                conn.close()
        else:
            flash('Error al conectar a la base de datos')
            return redirect(url_for('profile', id=alumno_id))  # Redirigir al perfil del estudiante sin cambios
    else:
        flash('Método no permitido')
        return redirect(url_for('index'))  # Redirigir al inicio si no se utiliza el método POST

@app.route('/perfil/alumno/cambiar_cinta', methods=['POST'])
@login_required
def cambiar_cinta():
    if request.method == 'POST':
        alumno_id = request.form.get('alumno_id')
        id_cinta = request.form.get('cinturon')

        if not alumno_id or not id_cinta:
            return 'ID del alumno o ID de la cinta no proporcionado.'

        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM Alumnos WHERE ID_alumno = ?", (alumno_id,))
                alumno = cursor.fetchone()
                if not alumno:
                    return f'No se encontró un alumno con el ID {alumno_id}.'

                cursor.execute("SELECT * FROM Cintas WHERE ID_cinta = ?", (id_cinta,))
                cinta = cursor.fetchone()
                if not cinta:
                    return f'No se encontró una cinta con el ID {id_cinta}.'

                cursor.execute("UPDATE Alumnos SET ID_cinta = ? WHERE ID_alumno = ?", (id_cinta, alumno_id))
                conn.commit()

                return redirect(f'/perfil/alumno/{alumno_id}')
            except pyodbc.Error as e:
                app.logger.error(f"[ERROR EN EL PROGRAMA] Error al actualizar la cinta del alumno: {str(e)}")
                return f'Error al actualizar la cinta del alumno: {str(e)}'
            finally:
                conn.close()
        else:
            return 'Error al conectar a la base de datos'


"""
RUTAS RELACIONADAS AL LOGIN
"""

@login_manager.user_loader
def load_user(user_id : str):
    # llama al método estático en el modelo
    return User.get_user(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # si ya inició sesión, hay que redigirirlo al index
    if current_user.is_authenticated:
        return redirect(url_for('index')) 

    # creamos el formulario de login
    form = LoginForm()

    if request.method == 'GET':
        return render_template('login.html', message = None, form = form)
    
    if request.method == 'POST':
        if form.validate_on_submit():
            app.logger.info('[Formulario] - Login validado')
            # recuperamos información del formulario
            username = form.username.data
            password = form.password.data

            conn = create_connection()
            if conn is not None:
                try:
                    # buscamos en la base de datos el usuario
                    user = User.get_user(username)
                    if user is not None:
                        # checamos si la contraseña ingresada coincide (se comparan hashes)
                        if user.check_password(password):
                            # con esta función, Flask-Login reconoce que hemos iniciado sesión
                            login_user(user)
                            app.logger.info(f'Inicio se sesión exitoso: {user.id}') 
                            # en el form debe haber <input type="hidden" name="next" value="{{ request.args.get('next', '') }}" />
                            # si el usuario ingresa a una página no autorizada, se le redirige al login y al iniciar sesión,
                            # entonces lo mandamos a donde quería ingresar:
                            next = request.form.get('next')
                            if not next or urlparse(next).netloc != '':
                                # lo redirigimos al index
                                next = url_for('index')
                            return redirect(next)
                        #
                        # si la contraseña es incorrecta, mostrar error
                        flash('La contraseña es incorrecta', 'error')
                        return redirect(url_for('login'))
                    # si user is None, mostrar usuario no encontrado
                    flash('Usuario no encontrado', 'error')
                    return redirect(url_for('login'))
                #
                except pyodbc.Error as e: 
                    print(f"Error al manipular la base de datos: {str(e)}")
                finally: conn.close()
                #
                flash('Hubo un error al recuperar la información, vuelve a intentarlo.', 'error')
                return redirect(url_for('login'))
        else: # Si el formulario no fue validado por algún motivo
            app.logger.info('[Formulario] - [ERROR] - Formulario no validado:')
            if form.username.errors:
                app.logger.info(f'[Formulario] - [Field] - [Username]')
                for error in form.username.errors:
                    app.logger.info(f'[Formulario] - [Error-info] - {error}')
                    flash(error,'error')
            if form.password.errors:
                app.logger.info(f'[Formulario] - [ERROR] - [Password]')
                for error in form.password.errors:
                    app.logger.info(f'[Formulario] - [Error-info] - {error}')
                    flash(error,'error')
            #   #
            #flash('Hubo un error en el procesamiento del formulario. Vuelve a intentarlo.', 'error')
            return redirect(url_for('login'))
    #   
    # si la conexión falló o hubo una excepción, mostrar error
    flash('Los datos ingresados no son válidos, vuelve a intentarlo.', 'error')
    return redirect(url_for('login'))
    
@app.route('/registro', methods=['GET', 'POST'])
def registro():
     # si ya inició sesión, hay que redigirirlo al index
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # crear el modelo de formulario
    form = RegistroForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            nombres = capitalize_each(form.nombres.data)
            apellido_p = capitalize_each(form.apellido_paterno.data)
            apellido_m = capitalize_each(form.apellido_materno.data)
            username = form.username.data
            email = form.email.data
            password = form.password.data
            confirmar_password = form.confirm_password.data

            print(f'{password} != {confirmar_password}')
            if password != confirmar_password:
                flash('Las contraseñas no coinciden, asegúrate de volver a escribirla correctamente.', 'error')
                return render_template('register.html', form=form) 
            
            password_hash = generate_password_hash(password)
            conn = create_connection()
            if conn is not None:
                try:
                    cursor = conn.cursor()
                    existent_user = User.get_user(username)
                    if existent_user is not None:
                        flash('Ya existe un usuario con este nombre de usuario.', 'error')
                        app.logger.warning('Ya existe un usuario con este username. Registro inválido')
                        return render_template('register.html', form = form) 
                    else:
                        query_insert = 'INSERT INTO Users (Username, Password, Email, Nombres, Ap_pat, Ap_mat, Fecha_creacion)\
                                        VALUES (?, ?, ?, ?, ?, ?, GETDATE())'
                        params = (username, password_hash, email, nombres, apellido_p, apellido_m,)
                        cursor.execute(query_insert, params)
                        cursor.commit()
                        app.logger.warning(f'[REGISTRO => {datetime.now()}] Registro completado con éxito: username - {username}')
                        # flash() guarda un mensaje que sólo será visto en la siguiente solicitud y se elimina
                        flash('Registro completado con éxito', 'success') 
                        return redirect(url_for('login'))
                    
                except pyodbc.Error as e:
                    print(f"Error manipular la base de datos: {str(e)}")
                finally:
                    conn.close()
        else:
            flash('Formulario no validado, vuelve a intentarlo.', 'error')
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
    return(redirect(url_for('index')))

"""
PERFIL DE ALUMNOS
"""

@app.route('/perfil/alumno/<int:id>', methods = ['GET'])
@login_required
def profile(id : int):
    conn = create_connection()
    if conn is not None:
        try:
            alumno = Alumno.get_by_id(id, current_user=current_user)
            if alumno is not None:
                if alumno.estatus == 'BAJA':
                    flash(f'Se intentó acceder a un pefil que ya fue dado de baja', 'error')
                    return redirect(url_for('mostrar_todos_los_alumnos')) 

                # son lo que le pasaremos al jinja
                info_pagos = None
                asistencias = None
                historial_adeudos = None
                historial_abonos = None

                cursor = conn.cursor()
                consulta_pagos = """
                    SELECT Pago_alumno.ID_pago_alumno as id_transaccion,
                        Pagos.Monto as Monto_total,
                        Pago_alumno.Abono as Meses_abonados,
                        Pago_alumno.Adeudo as Meses_adeudados,
                        Pagos.Fecha_pago, Pagos.Fecha_corte,
                        Pagos.Monto,
                        Pago_alumno.Meses_abono, Pago_alumno.Meses_adeudo
                    FROM Pagos, Pago_alumno, Alumnos
                    WHERE Alumnos.ID_alumno = ? AND Pago_alumno.Estatus = 1
                        AND Pago_alumno.ID_pago = Pagos.ID_pago
                        AND Alumnos.ID_alumno = Pago_alumno.ID_alumno
                    ORDER BY pagos.Fecha_pago DESC
                """
                #region old
                # consulta_pagos = """
                #     SELECT Pago_alumno.ID_pago_alumno as id_transaccion,
                #         dp.Dia as Dia_pago, 
                #         mp.Mes as Mes_pago,
                #         ap.Anio as Anio_pago, 
                #         Pagos.Monto as Monto_total,
                #         Pago_alumno.Abono, Pago_alumno.Adeudo,  
                #         Pago_alumno.Meses_abono as Meses_abonados,
                #         Pago_alumno.Meses_adeudo as Meses_adeudados,
                #         dc.Dia as Dia_corte, 
                #         mc.Mes as Mes_corte, 
                #         ac.Anio as Anio_corte
                #     FROM Pagos, Pago_alumno, Alumnos, 
                #         Dias_pago dp, Dias_pago dc, 
                #         Meses_pago mp, Meses_pago mc, 
                #         Anios_pago ap, Anios_pago ac
                #     WHERE Alumnos.ID_alumno = ? AND Pago_alumno.Estatus = 1
                #         AND Pago_alumno.ID_pago = Pagos.ID_pago
                #         AND Alumnos.ID_alumno = Pago_alumno.ID_alumno
                #         AND Pagos.ID_dia_pago = dp.ID_dia
                #         AND Pagos.ID_dia_corte = dc.ID_dia
                #         AND Pagos.ID_mes_pago = mp.ID_mes
                #         AND Pagos.ID_mes_corte = mc.ID_mes
                #         AND Pagos.ID_anio_pago = ap.ID_anio
                #         AND Pagos.ID_anio_corte = ac.ID_anio
                #     ORDER BY ap.Anio DESC,
                #         mp.ID_mes DESC,
                #         dp.Dia DESC
                #     """
                #endregion
                params = (id,)
                cursor.execute(consulta_pagos, params)
                resultados = cursor.fetchall()
                
                # consultar todos los pagos en este nivel
                if resultados is not None:
                    info_pagos = []
                    for registro in resultados:
                        info_pagos.append(registro)

                # consultar las asistencias
                consulta_asistencias = """       
                SELECT 
                    Dias_semana.Dia as Dia_sem, Horas.Hora, 
                    Dias_semana.ID_dia as id_dia_sem, Horas.ID_hora as id_hora,
                    Asistencias.fecha  as fecha
                FROM Asistencias, Alumnos, Clases, Dias_semana, Horas
                WHERE Alumnos.ID_alumno = Asistencias.ID_alumno
                    AND Asistencias.ID_clase = Clases.ID_clase
                    AND Clases.ID_dia_semana = Dias_semana.ID_dia
                    AND Clases.ID_hora = Horas.ID_hora
                    AND Alumnos.ID_alumno = ?
                    #AND Asistencias.Estatus = 1
                ORDER BY asistencias.Fecha DESC, 
                        Horas.ID_hora
                """
                #region old
                # consulta_asistencias = """
                # SELECT Dias_asist.Dia, Meses_asist.Mes, Anios_asist.Anio, Meses_asist.ID_mes,
                #     Dias_semana.Dia as Dia_sem, Horarios.Hora, 
                #     Dias_semana.ID_dia_sem as id_dia_sem, Horarios.ID_hora as id_hora
                # FROM Alumno_clase, Alumnos, Dias_asist, Meses_asist, 
                #     Anios_asist, Clases, Dias_semana, Horarios
                # WHERE Alumnos.ID_alumno = Alumno_clase.ID_alumno
                #     AND Alumno_clase.ID_dia_asist = Dias_asist.ID_dia
                #     AND Alumno_clase.ID_mes_asist = Meses_asist.ID_mes
                #     AND Alumno_clase.ID_anio_asist = Anios_asist.ID_anio
                #     AND Alumno_clase.ID_clase = Clases.ID_clase
                #     AND Clases.ID_dia_semana = Dias_semana.ID_dia_sem
                #     AND Clases.ID_hora = Horarios.ID_hora
                #     AND Alumnos.ID_alumno = ?
                #     AND Alumno_clase.Estatus = 1
                # ORDER BY Anios_asist.Anio DESC, 
                #         Meses_asist.ID_mes DESC, 
                #         Dias_asist.ID_dia DESC, 
                #         Horarios.ID_hora
                # """
                #endregion
                # la idea es que en la página se pueda elegir cuántas asistencias mostrar por página
                # los datos se envian en la url como args ,pero tienen valores por defecto si no hay
                # page = request.args.get('page', 0)
                # elems_per_page = request.args.get('items', 30)
                params = (id,)
                cursor.execute(consulta_asistencias, params)
                selected_asistencias = cursor.fetchall()
                if selected_asistencias is not None:
                    asistencias = []
                    for asistencia in selected_asistencias:
                        asistencias.append(asistencia)
                        # se guarda cada asistencia en una lista

                # hay que pasarle un objeto de los formularios para
                # poder mostrarlos y renderizar sus campos en el html
                form = EditarAlumnoForm()
                pago = None
                asist = RegistrarAsistenciaForm()
                print(alumno)
                print(info_pagos)
                return render_template('perfil.html', user = current_user, form=form, pagoForm = pago, asistenciaForm = asist, alumno = alumno, info_pagos=info_pagos, lista_asistencia=asistencias, historial_adeudos=historial_adeudos, historial_abonos=historial_abonos)

            flash(f'El perfil del alumno no existe o no tiene los permisos para visualizarlo', 'error')
            return redirect(url_for('mostrar_todos_los_alumnos'))
        except pyodbc.Error as e:
            app.logger.error(f"[ERROR EN EL PROGRAMA] Error al ejecutar la consulta: {str(e)}")
            flash(f'Error al recuperar la información del alumno', 'error')
            return redirect(url_for('mostrar_todos_los_alumnos')) 
        finally:
            conn.close()
    else:
        flash(f'Error al conectar a la base de datos', 'error')
        return redirect(url_for('mostrar_todos_los_alumnos')) 

"""
CONSULTAS DE LOS PAGOS
"""

# consulta compleja
@app.route('/consultas/pagos/deudores', methods = ['GET'])
@login_required
def consultar_deudores():
    alumnos = Alumno.get_all(True, current_user=current_user)
    deudores = []
    for alumno in alumnos:
        query = """
            SELECT historial_abonos.Fecha_abono
            FROM Pago_alumno
                JOIN Historial_abonos on Pago_alumno.ID_pago_alumno = Historial_abonos.ID_pago_alumno
            WHERE Pago_alumno.ID_pago_alumno = (
                SELECT pago_alumno.ID_pago_alumno
                FROM pago_alumno
                JOIN pagos ON pago_alumno.ID_pago = pagos.ID_pago
                WHERE pago_alumno.ID_alumno = 3
                    AND pago_alumno.Estatus = 1
                ORDER BY pagos.Fecha_pago DESC
                LIMIT 1
            )
            ORDER BY Historial_abonos.Fecha_abono DESC
            """
        params = (alumno.id,)
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute(query, params)
            ultimo_mes = cursor.fetchone()
            if ultimo_mes is not None:
                # ver_atributos(ultimo_mes)
                mes = int(ultimo_mes.ID_mes)
                anio = int(ultimo_mes.Anio)
                fecha_actual = datetime.now().date()
                fecha_previa = datetime.strptime(nums_to_str_date(1, mes, anio), '%Y-%m-%d').date()
                # print(fecha_actual)
                # print(fecha_previa)

                if (anio, mes) < (fecha_actual.year, fecha_actual.month):
                    print(f'Último mes pagado: {mes}, Año: {anio}\nMes actual: {fecha_actual.month}, Año actual: {fecha_actual.year}')
                    
                    numero = diferencia_meses(fecha_actual, fecha_previa)

                    print(f'No se ha pagado el periodo actual, debe {numero} meses')
                    setattr(alumno, 'mes', ultimo_mes.Mes)
                    setattr(alumno, 'anio', ultimo_mes.Anio)
                    setattr(alumno, 'meses_adeudados', numero)
                    deudores.append(alumno)
    for d in deudores:
        print(d.nombres)
    return render_template('pagos_completos.html', user = current_user, alumnos = deudores)

"""
FUNCIONES PARA LOS PAGOS
"""

@app.route('/consultas/pagos/post', methods = ['POST'])
@login_required
def agregar_pago_post():
    form = ValidarPagoForm()

    id_alumno = form.id_alumno.data
    alumno = Alumno.get_by_id(int(id_alumno))
    if alumno is not None:
        if form.validate_on_submit():
            fecha_corte = form.fecha_corte.data
            fecha_pago = form.fecha_pago.data
            monto = form.monto.data
            abono = form.abono.data
            adeudo = form.adeudo.data
            cant_meses_abonados = form.cant_meses_abonados.data
            cant_meses_adeudados = form.cant_meses_adeudados.data

            lista_meses_abono = request.form.getlist('meses_abonados[]')
            lista_meses_adeudos = request.form.getlist('meses_adeudados[]')
            
            params = (id_alumno, fecha_pago, fecha_corte, float(monto), float(abono), float(adeudo), cant_meses_abonados, lista_meses_abono, cant_meses_adeudados, lista_meses_adeudos)
            print(f'Params: {params}')

            # return redirect(url_for('consulta', id_alumno = id_alumno))
        
            conn = create_connection()
            if conn is not None:
                try:
                    cursor = conn.cursor()

                    id_anio_pago = int(str(fecha_pago.year)[-2:])
                    id_anio_corte = int(str(fecha_corte.year)[-2:])

                    insertar_pago = """
                        INSERT INTO Pagos (Monto, ID_dia_pago, ID_mes_pago, ID_anio_pago, ID_dia_corte, ID_mes_corte, ID_anio_corte)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """
                    params = (float(monto), fecha_pago.day, fecha_pago.month, id_anio_pago, fecha_corte.day, fecha_corte.month, id_anio_corte)
                    print(params)
                    cursor.execute(insertar_pago, params)
                    id_pago = cursor.execute('SELECT @@IDENTITY as ID').fetchone()[0]
                    print(id_pago)
                    if id_pago is not None:
                        insertar_pago_alumno = """
                            INSERT INTO Pago_alumno (Abono, Adeudo, Meses_abono, Meses_adeudo, ID_pago, ID_alumno)    
                            VALUES (?, ?, ?, ?, ?, ?)
                            """
                        params = (abono, adeudo, cant_meses_abonados, cant_meses_adeudados, id_pago, id_alumno)
                        cursor.execute(insertar_pago_alumno, params)
                        
                        id_pago_alumno = cursor.execute('SELECT @@IDENTITY as ID').fetchone()[0]
                        # print(id_pago_alumno)
                        print('A PARTIR DE AQUI SE DEBEN CREAR LOS HISTORIALES')

                        if cant_meses_abonados > 0:
                            for mes in lista_meses_abono:
                                fecha = parsear_fecha(f'{mes}-01')
                                id_anio = int(str(fecha.year)[-2:])
                                insertar_abonos = """
                                    INSERT INTO Historial_abonos (ID_pago_alumno, ID_mes, ID_anio)
                                    VALUES (?, ?, ?)
                                    """
                                params = (id_pago_alumno, fecha.month, id_anio)
                                cursor.execute(insertar_abonos, params)
                        else: print('Por qué no hay meses abonados?')

                        if cant_meses_adeudados > 0:
                            for mes in lista_meses_adeudos:
                                fecha = parsear_fecha(f'{mes}-01')
                                id_anio = int(str(fecha.year)[-2:])
                                insertar_adeudos = """
                                    INSERT INTO Historial_adeudos (ID_pago_alumnos, ID_mes, ID_anio)
                                    VALUES (?, ?, ?)
                                    """
                                params = (id_pago_alumno, fecha.month, id_anio)
                                cursor.execute(insertar_adeudos, params)
                        else: print('Por qué no hay meses adeudados? O es el primer pago?')

                        cursor.commit()
                        print('Debió funcionar')
                        flash('El pago fue dado de alta con éxito. Revisa el detalle del pago para más información.', 'success')
                        return redirect(url_for('profile', id = id_alumno))
                #
                except pyodbc.DatabaseError as e:
                    conn.rollback()
                    print('checar si se hizo rollback')
                    print(str(e))
                finally:
                    conn.close()
        else: # Si el formulario no fue validado por algún motivo
            flash('Hubo un error al procesar la operación, vuelve a intentarlo', 'error')
            app.logger.error('[Formulario] - [ERROR] - Formulario no validado:')
            if form.errors:
                for error in form.errors:
                    app.logger.error(f'[Formulario] - [Error-info] - {error}')
    else:
        flash('Intentó agregar un pago a un alumno que no existe o que no tiene los permisos para modificar', 'error')
        return redirect(url_for('mostrar_todos_los_alumnos'))

    return redirect(url_for('agregar_pago', id_alumno = id_alumno))

@app.route('/consultas/pagos/nuevo/<id_alumno>', methods=['GET'])
@login_required
def agregar_pago(id_alumno):
    alumno = Alumno.get_by_id(id_alumno)
    if alumno is None:
        flash('El alumno no existe o no tiene los permisos para modificarlo', 'error')
        return redirect(url_for('mostrar_todos_los_alumnos'))
    
    paquete = None
    form = ValidarPagoForm()
    conn = create_connection()
    if conn is not None:
        consultar_ultimo_pago = """
            SELECT DAY(Pagos.Fecha_pago) as Dia, MONTH(Pagos.Fecha_pago) as Mes, YEAR(Pagos.Fecha_pago) as Anio, Pago_alumno.*, Historial_abonos.* 
            FROM Pago_alumno, Historial_abonos, Pagos
            WHERE Pago_alumno.ID_alumno = ?
                AND Pago_alumno.Estatus = 1
                AND Pago_alumno.ID_pago_alumno = Historial_abonos.ID_pago_alumno
                AND Pago_alumno.ID_pago = Pagos.ID_pago
            ORDER BY Pagos.Fecha_pago DESC
            """
        params = (id_alumno,) # id alumno 1
        
        cursor = conn.cursor()
        cursor.execute(consultar_ultimo_pago, params)
        ultimo_pago = cursor.fetchone()

        # Si existe un último pago
        if ultimo_pago:
            # Revisar cuál fue el último mes abonado (el más actual)
            consultar_ultimo_mes_abonado = """
                SELECT Pago_alumno.Id_pago_alumno as ID, MONTH(Historial_abonos.Fecha_abono) as Mes, YEAR(Historial_abonos.Fecha_abono) AS Anio
                FROM Pago_alumno
                    JOIN Historial_abonos on Pago_alumno.ID_pago_alumno = Historial_abonos.ID_pago_alumno
                WHERE Pago_alumno.ID_pago_alumno = ?
                ORDER BY Historial_abonos.Fecha_abono DESC
                """
            params = (ultimo_pago[3],)
            cursor.execute(consultar_ultimo_mes_abonado, params)
            ultimo_mes_pagado = cursor.fetchone()
            # Si se consiguió el último mes abonado
            if ultimo_mes_pagado is not None:
                # calcularemos los meses que hay entre el último pagado y el que debe pagar ahora
                fecha_previa = datetime.strptime(nums_to_str_date(1, ultimo_mes_pagado[1], ultimo_mes_pagado[2]), '%Y-%m-%d').date()
                fecha_actual = datetime.now().date()

                # en principio debe pagar 1 mes de abono
                cantidad_meses_abono = 1 

                meses = diferencia_meses(fecha_actual, fecha_previa)
                # si los meses son negativos, es que ya se pasó de la fecha actual, es decir, adelantó meses
                if meses <= 0:
                    meses = 0
                    cantidad_meses_abono = 0
                print(f'Debe {meses} meses desde el último pago registrado, el último se paga como abono')
                
                # el mes a abonar es el último (el de este mes)
                # los meses adeudados son los que quedan en medio (si es que hay)
                cantidad_meses_adeudo = meses - 1
                if cantidad_meses_adeudo < 0: 
                    cantidad_meses_adeudo = 0


                meses_adeudo = [] # ========== VAR
                meses_abono = []
                # meses abono en realidad sólo guarda el pago actual
                # pero a partir de este se pueden calcular los siguientes si quiere abonar
                if cantidad_meses_abono > 0:
                    meses_abono = [{
                            'id_mes':fecha_actual.month,
                            'mes':nombre_mes(fecha_actual.month),
                            'id_anio': int(str(fecha_actual.year)[-2:]),
                            'anio':fecha_actual.year,
                            'str': f'{fecha_actual.year}-{str(fecha_actual.month).zfill(2)}'
                        }]
                
                # esto calcula los pagos en medio que debe y los guarda en meses_adeudo
                print(f'El último pago fue de {nombre_mes(fecha_previa.month)}-{fecha_previa.year}')
                current_anio = fecha_previa.year # ========== VAR
                for index in range(fecha_previa.month + 1, fecha_actual.month):
                    if index > 12:
                        m = index % 12
                        current_anio += int(index / 12)
                    else: current_mes = index
                    meses_adeudo.append( {
                        'id_mes':current_mes,
                        'mes':nombre_mes(current_mes),
                        'id_anio': int(str(current_anio)[-2:]),
                        'anio':current_anio,
                        'str': f'{current_anio}-{str(current_mes).zfill(2)}'
                    } ) # ========== VAR
                    print(f'Debe {nombre_mes(current_mes)}-{current_anio} ')
                print(f'Este mes debe abonar {nombre_mes(fecha_actual.month)}-{fecha_actual.year}')

                # calcula la fecha de corte
                fecha_corte = datetime.today().date() + relativedelta(day=1)
                fecha_corte += relativedelta(months=1)

                # todos los datos los empaqueta para mandar
                paquete = {
                    'tiene_pagos': True,
                    'fecha_ultimo_pago': datetime.strptime(nums_to_str_date(1, ultimo_mes_pagado[1]+1, ultimo_mes_pagado[2]), '%Y-%m-%d').date(),
                    'fecha_actual': fecha_actual,
                    'fecha_corte': fecha_corte,
                    'id_alumno': id_alumno,
                    'cant_meses_abonados': cantidad_meses_abono,
                    'meses_abonados': meses_abono,
                    'cant_meses_adeudados': cantidad_meses_adeudo,
                    'meses_adeudados': meses_adeudo
                }
                # Información de pago recuperada con éxito
                app.logger.info('Información de pago recuperada con éxito')
                return render_template('testeando-form-pago.html', form=form, paquete=paquete, alumno=alumno)

            else: 
                app.logger.warn('Se encontró un pago, pero no se encontró detalle del mismo')
        else: 
            # Aquí habría que poner que pueda poner el primer pago
            fecha_actual = datetime.now().date()
            fecha_corte = datetime.today().date() + relativedelta(day=1)
            fecha_corte += relativedelta(months=1)
            paquete = {
                'tiene_pagos': False,
                'fecha_ultimo_pago': None,
                'fecha_actual': fecha_actual,
                'fecha_corte': fecha_corte,
                'id_alumno': id_alumno,
                'cant_meses_abonados': 0,
                'meses_abonados': 0,
                'cant_meses_adeudados': 0,
                'meses_adeudados': 0
            }

            # El alumno no cuenta con ningún pago, ingresa el primer pago
            print('El alumno no cuenta con ningún pago, ingresa el primer pago')
            app.logger.info('El alumno no cuenta con ningún pago, ingresa el primer pago')
            return render_template('testeando-form-pago.html', form=form, paquete=paquete, alumno=alumno)
        
    # No se pudo conectar a la base de datos
    app.logger.error('Se encontró un pago, pero no se encontró detalle del mismo')
    return render_template('testeando-form-pago.html', form=form, paquete=paquete, alumno=alumno)

@app.route('/consultas/pagos/eliminar', methods=['POST'])
@login_required
def eliminar_pago():

    id_alumno = request.form.get('id_alumno')
    id_pago_alumno = request.form.get('id_pago_alumno')

    if id_alumno is not None:
        alumno = Alumno.get_by_id(int(id_alumno))
        if alumno is None:
            flash('El alumno no existe o no tiene los permisos para modificarlo', 'error')
            return redirect(url_for('mostrar_todos_los_alumnos'))
        #
        else:
            conn = create_connection()
            if conn is not None:
                try:
                    encontrar_pago_alumno = """
                        SELECT * FROM Pago_alumno WHERE ID_pago_alumno = ?
                        """
                    params = (id_pago_alumno)

                    cursor = conn.cursor()
                    cursor.execute(encontrar_pago_alumno, params)
                    pago_alumno = cursor.fetchone()
                    if pago_alumno is not None:

                        ocultar_pago_alumno = """
                            UPDATE Pago_alumno SET Estatus = 0 WHERE ID_pago_alumno = ?
                            """
                        cursor.execute(ocultar_pago_alumno, params)
                        ocultar_pago = """
                            UPDATE Pagos SET Estatus = 0 WHERE ID_pago = ?               
                            """
                        params = (pago_alumno.ID_pago)
                        cursor.execute(ocultar_pago, params)
                        cursor.commit()
                        print('Debió funcionar')
                        flash('Se eliminó el pago del alumno exitosamente', 'success')
                        return redirect(url_for('profile', id = id_alumno))

                except pyodbc.Error as e:
                    print(f'[ERROR] - {str(e)}')
                finally:
                    if conn is not None:
                        conn.close()

            flash('Hubo un problema relacionado con la base de datos', 'error')
            return redirect(url_for('profile', id = id_alumno))
    
    print('No se mandó una solicitud correcta')
    return redirect(url_for('profile', id = id_alumno))

"""
MÉTODOS PARA LAS ASISTENCIAS
"""

@app.route('/perfil/alumno/registrar_asistencia', methods=['POST'])
@login_required
def registrar_asistencia():
    # validar el formulario
    form = RegistrarAsistenciaForm()
    if form.validate_on_submit():
        # obtener los datos
        id_alumno = form.id_alumno.data
        fecha_asistencia = form.fecha_asistencia.data
        # fecha_asistencia = f'{form.fecha_asistencia.data.year}-{form.fecha_asistencia.data.month}-{form.fecha_asistencia.data.day}'
        dia_clase = form.dia_clase.data
        hora_clase = form.hora_clase.data

        app.logger.warning(f'INFORMACIÓN ENVIADA EN LA NUEVA ASISTENCIA: {(id_alumno, fecha_asistencia, dia_clase, hora_clase)}')
        #return redirect(url_for('profile', id=id_alumno))

        #primero verificar que el alumno existe
        alumno_exist = Alumno.get_by_id(id_alumno, current_user=current_user)
        if alumno_exist is None:
            app.logger.warning('El alumno no existe o no tiene los permisos para modificarlo')
            flash('No existe un alumno con la ID ingresada')
            return redirect(url_for('mostrar_todos_los_alumnos'))

        # primero verificar que exista la clase en la BD
        consulta_clase = """
            SELECT Clases.ID_clase  as id_clase, Dias_semana.Dia as dia_sem, Horas.hora
            FROM Clases 
                JOIN Dias_semana ON Clases.ID_dia_semana = Dias_semana.ID_dia
                JOIN Horas ON Clases.ID_hora = Horas.ID_hora
            WHERE Dias_semana.ID_dia = ?
                AND Horas.ID_hora = ?
            """
        params = (dia_clase, hora_clase)
        conn = create_connection()
        if conn is not None:
            try:
                cursor=conn.cursor()
                cursor.execute(consulta_clase, params)
                clase = cursor.fetchone()
                if clase is None:
                    app.logger.warning('No existe la clase que se intentó registrar')
                    flash('No existe la clase que se intentó registrar.', 'error')
                    return redirect(url_for('profile', id=id_alumno))

                # aquí habría que ver que no se pueda duplicar una asistencia
                params = (id_alumno, clase[0], fecha_asistencia) #clase[0] = id_clase
                print(clase)
                existe_asistencia = """
                    SELECT ID_alumno, ID_clase, Fecha
                    FROM Asistencias
                    WHERE ID_alumno = ? and ID_clase = ? and Fecha = ?
                    """
                cursor.execute(existe_asistencia, params)
                asistencia = cursor.fetchone()
                if asistencia is not None:
                    flash(f'No se permite duplicar asistencias: Ya hay una asistencia registrada de {alumno_exist.nombres} {alumno_exist.apellido_paterno} en la clase del día {clase[1]} {str(fecha_asistencia)} a las {clase[2]} hrs.', 'error')
                    return redirect(url_for('profile', id=id_alumno))
                    
                # si la clase y el alumno existen, entonces se puede insertar la asistencia
                insertar_asistencia = """
                    INSERT INTO Asistencias (ID_alumno, ID_clase, Fecha)
                    VALUES (?, ?, ?)
                    """
                cursor.execute(insertar_asistencia, params)
                flash(f'Se ha registrado la asistencia del alumno {alumno_exist.nombres} {alumno_exist.apellido_paterno} del {clase[1]} {str(fecha_asistencia)} a las {clase[2]}', 'success')
                conn.commit()
                return redirect(url_for('profile', id=id_alumno))
            except pyodbc.Error as e:
                flash('Error al consultar la base de datos', 'error')
                app.logger.error(f"[ERROR AL CONSULTAR LA BD] - Consulta: {str(e)}")
            finally: 
                conn.close()

        flash('No se pudo conectar a la base de datos', 'error')
    flash('El formulario no fue validado correctamente, se rechaza la asistencia', 'error')
    return redirect(url_for('profile', id=id_alumno))


@app.route('/perfil/alumno/eliminar_asistencia', methods=['POST'])
@login_required
def eliminar_asistencia():
    # obtener los datos
    id_alumno = request.form.get('id_alumno_eliminar', -1)
    fecha_asistencia = datetime.strptime(request.form.get('fecha_eliminar', '2000-01-01'), '%Y-%m-%d')
    dia_clase = request.form.get('dia_eliminar', -1)
    hora_clase = request.form.get('hora_eliminar', -1)

    # ver si el alumno existe
    alumno = Alumno.get_by_id(id_alumno)
    if alumno is None:
        app.logger.error(f'El alumno no existe o no tiene los permisos para modificarlo')
        flash(f'El alumno no existe o no tiene los permisos para modificarlo', 'error')
        return redirect(url_for('mostrar_todos_los_alumnos')) 
    else:
        #
        conn = create_connection()
        if conn is not None:
            try:
                # vemos si la clase existe y sacamos su id
                consultar_clase = """
                    SELECT Clases.ID_clase as id, Dias_semana.Dia, Horas.Hora
                    FROM Clases JOIN Dias_semana ON Clases.ID_dia_semana = Dias_semana.ID_dia
                                JOIN horas ON Clases.ID_hora = Horas.ID_hora
                    WHERE Clases.ID_dia_semana = ? AND Clases.ID_hora = ?
                    """
                params = (dia_clase, hora_clase)
                cursor = conn.cursor()
                cursor.execute(consultar_clase, params)
                clase = cursor.fetchone()
                if clase is None:
                    app.logger.error(f'No se encontró la clase del {clase[1]} a las {clase[2]} hrs.')
                    flash(f'No se encontró la clase del {clase[1]} a las {clase[2]} hrs.', 'error')
                    return redirect(url_for('profile', id=alumno.id)) 
                # si la clase existe, ver si existe la asistencia
                consultar_asistencia = """
                    SELECT ID_asistencia as id, Fecha
                    FROM Asistencias
                    WHERE Asistencias.ID_alumno = ?
                        AND asistencias.Fecha = ?
                        AND Asistencias.ID_clase = ?
                    """
                params = (alumno.id, fecha_asistencia, clase[0])
                cursor.execute(consultar_asistencia, params)
                asistencia = cursor.fetchone()
                if asistencia is None:
                    app.logger.error(f'No se encontró la asistencia del {clase[1]} {fecha_asistencia.day} de {fecha_asistencia.month} del {fecha_asistencia.year} a las {clase[2]} hrs.')
                    flash(f'No se encontró la asistencia de {alumno.nombres} {alumno.apellido_paterno} del {clase[1]} {str(fecha_asistencia)} a las {clase[2]} hrs.', 'error')
                    return redirect(url_for('profile', id=alumno.id)) 
                
                # BORRAR
                # consulta_eliminar = 'UPDATE Alumno_clase SET Estatus = 0 WHERE ID_alumno_clase = ?'
                # params = (asistencia.id)
                # cursor.execute(consulta_eliminar, params)
                consulta_eliminar = 'DELETE FROM Asistencias WHERE ID_asistencia = ?'
                params = (asistencia[0],)
                cursor.execute(consulta_eliminar, params)

                app.logger.info(f'Se eliminó la asistencia del {clase[1]} {fecha_asistencia.day} de {fecha_asistencia.month} del {fecha_asistencia.year} a las {clase[2]} hrs.')
                conn.commit()
                flash(f'Se eliminó la asistencia de {alumno.nombres} {alumno.apellido_paterno} del {clase[1]} {fecha_asistencia.day} de {fecha_asistencia.month} del {fecha_asistencia.year} a las {clase[2]} hrs.', 'success')
                return redirect(url_for('profile', id=alumno.id)) 
            except pyodbc.DatabaseError as e:
                app.logger.error(f'[ERROR EN LA DB] - {str(e)}')
            #
            finally: conn.close()
            flash('Error al consultar la base de datos.', 'error')
            return redirect(url_for('profile', id=alumno.id)) 
        #
        app.logger.error('Error al conectar la base de datos.')
        flash('Error al conectar la base de datos.', 'error')
        return redirect(url_for('profile', id=alumno.id)) 

"""
DEFINIENDO FUNCIONES DE TIPO API, QUE REGRESAN JSON CON INFORMACIÓN
ESTAS FUNCIONES ESTÁN PENSADAS PARA HACER UNA AJAX.REQUEST CON JAVASCRIPT
"""
# esta api puede usarse con javascript para recuperar los horarios
# de un día de la semana dado (id_dia) y añadir nuevas asistencias
@app.route('/api/horarios/<id_dia>', methods = ['GET'])
def recuperar_horario(id_dia):
    conn = create_connection()
    if conn is not None:
        try:
            consulta = """
                SELECT Dias_semana.ID_dia as id_dia, Dias_semana.Dia as dia, Horas.ID_hora as id_hora, Horas.Hora as hora 
                FROM Clases 
                    INNER JOIN Dias_semana ON Clases.ID_dia_semana = Dias_semana.ID_dia
                    INNER JOIN Horas ON Clases.ID_hora = Horas.ID_hora 
                WHERE Dias_semana.ID_dia = ?
                """
            params = (id_dia,)
            cursor = conn.cursor()
            cursor.execute(consulta, params)
            horarios = cursor.fetchall()
            if horarios is not None:
                horas = fetch_all_to_dict_list(horarios, cursor)
                return jsonify(horas) # se JSONifica y regresa la cadena
            return jsonify(None) # Regresar un JSON vacío
        except pyodbc.Error as e:
            app.logger.error(f"[ERROR AL CONSULTAR LA BD] - Consulta: {str(e)}")
        finally: 
            conn.close()
    return jsonify(None) # regresar un JSON vacío

@app.route('/api/historial/adeudos/<id_pago_alumno>', methods = ['GET'])
def consultar_detalle_adeudos(id_pago_alumno):
    conn = create_connection()
    if conn is not None:
        try:
            query = """
            SELECT MONTH(historial_adeudos.Fecha_adeudo), YEAR(historial_adeudos.Fecha_adeudo)
            FROM Alumnos, Pago_alumno, Historial_adeudos
            WHERE Alumnos.ID_alumno = Pago_alumno.ID_alumno
                AND Pago_alumno.ID_pago_alumno = Historial_adeudos.ID_pago_alumno
                AND Historial_adeudos.ID_pago_alumno = ?
            """
            params = (id_pago_alumno,)
            cursor = conn.cursor()
            cursor.execute(query, params)
            historial_adeudo = cursor.fetchall()
            if historial_adeudo is not None:
                historial = fetch_all_to_dict_list(historial_adeudo, cursor)
                return jsonify(historial)
            return jsonify(None) # Regresar un JSON vacío
        except pyodbc.Error as e:
            app.logger.error(f"[ERROR EN EL PROGRAMA] Error al ejecutar la consulta: {str(e)}")
        finally: 
            conn.close()
    return jsonify(None)

@app.route('/api/historial/abonos/<id_pago_alumno>', methods = ['GET'])
def consultar_detalle_abonos(id_pago_alumno):
    conn = create_connection()
    if conn is not None:
        try:
            consulta_abonos = """
                SELECT MONTH(historial_abonos.Fecha_abono) as Nombre_mes, YEAR(historial_abonos.Fecha_abono) as Anio
                FROM Alumnos, Pago_alumno, historial_abonos
                WHERE Alumnos.ID_alumno = Pago_alumno.ID_alumno
                    AND Pago_alumno.ID_pago_alumno = historial_abonos.ID_pago_alumno
                    AND historial_abonos.ID_pago_alumno = ?
                """
            params = (id_pago_alumno,)
            cursor = conn.cursor()
            cursor.execute(consulta_abonos, params)
            historial_abonos = cursor.fetchall()
            if historial_abonos is not None:
                historial = fetch_all_to_dict_list(historial_abonos, cursor)
                return jsonify(historial)
            return jsonify(None)
        except pyodbc.Error as e:
            app.logger.error(f"[ERROR EN EL PROGRAMA] Error al ejecutar la consulta: {str(e)}")
        finally: conn.close()
    return jsonify(None)

"""
ESTA RUTA ES DE PRUEBAS, SÓLO EXISTE PARA PODER METER PAGOS ANTERIORES SIN LAS VALIDACIONES
"""
@app.route('/ponerpagos/<id_alumno>')
def ponerPagos(id_alumno):
    alumno = Alumno.get_by_id(id_alumno)
    if alumno is None:
        flash('No se encontró el alumno', 'error')
        return redirect(url_for('mostrar_todos_los_alumnos'))
    
    paquete = None
    form = ValidarPagoForm()
    conn = create_connection()
    if conn is not None:
        consultar_ultimo_pago = """
            select Pagos.ID_dia_pago as Dia, Pagos.ID_mes_pago as Mes, Anios_pago.Anio as Anio, Pago_alumno.*, Historial_abonos.* 
            from Pago_alumno, Historial_abonos, Pagos, Anios_pago
            where
                Pagos.ID_anio_pago = Anios_pago.ID_anio
            and Pago_alumno.ID_alumno = ?
            and Pago_alumno.ID_pago_alumno = Historial_abonos.ID_pago_alumno
            and Pago_alumno.ID_pago = Pagos.ID_pago
            ORDER BY Pagos.ID_anio_pago DESC, 
                    Pagos.ID_mes_pago DESC, 
                    Pagos.ID_dia_pago DESC
            """
        params = (id_alumno,) # id alumno 1
        
        cursor = conn.cursor()
        cursor.execute(consultar_ultimo_pago, params)
        ultimo_pago = cursor.fetchone()

        if ultimo_pago:
            consultar_ultimo_mes_abonado = """
                SELECT Pago_alumno.Id_pago_alumno as ID, Historial_abonos.ID_mes as Mes, Anios_abono.Anio
                FROM Pago_alumno
                    JOIN Historial_abonos on Pago_alumno.ID_pago_alumno = Historial_abonos.ID_pago_alumno
                    JOIN Anios_abono on Anios_abono.ID_anio = Historial_abonos.ID_anio	
                WHERE Pago_alumno.ID_pago_alumno = ?
                ORDER BY Anios_abono.Anio DESC,
                    Historial_abonos.ID_mes DESC
                """
            params = (ultimo_pago.ID_pago_alumno,)
            cursor.execute(consultar_ultimo_mes_abonado, params)
            ultimo_mes_pagado = cursor.fetchone()
            if ultimo_mes_pagado is not None:

                fecha_previa = datetime.strptime(nums_to_str_date(1, ultimo_mes_pagado.Mes, ultimo_mes_pagado.Anio), '%Y-%m-%d').date()
                fecha_actual = datetime.now().date()

                meses = diferencia_meses(fecha_actual, fecha_previa)
                print(f'Debe {meses} meses desde el último pago registrado, el último se paga como abono')
                
                cantidad_meses_adeudo = meses - 1
                if cantidad_meses_adeudo < 0: 
                    cantidad_meses_adeudo = 0

                cantidad_meses_abono = 1 
                if cantidad_meses_adeudo == 0:
                    cantidad_meses_abono = 0

                meses_adeudo = [] # ========== VAR
                meses_abono = []
                if cantidad_meses_abono > 0:
                    meses_abono = [{
                            'id_mes':fecha_actual.month,
                            'mes':nombre_mes(fecha_actual.month),
                            'id_anio': int(str(fecha_actual.year)[-2:]),
                            'anio':fecha_actual.year,
                            'str': f'{fecha_actual.year}-{str(fecha_actual.month).zfill(2)}'
                        }]
                
                print(f'El último pago fue de {nombre_mes(fecha_previa.month)}-{fecha_previa.year}')
                current_anio = fecha_previa.year # ========== VAR
                for index in range(fecha_previa.month + 1, fecha_actual.month):
                    if index > 12:
                        m = index % 12
                        current_anio += int(index / 12)
                    else: current_mes = index
                    meses_adeudo.append( {
                        'id_mes':current_mes,
                        'mes':nombre_mes(current_mes),
                        'id_anio': int(str(current_anio)[-2:]),
                        'anio':current_anio,
                        'str': f'{current_anio}-{str(current_mes).zfill(2)}'
                    } ) # ========== VAR
                    print(f'Debe {nombre_mes(current_mes)}-{current_anio} ')
                print(f'Este mes debe abonar {nombre_mes(fecha_actual.month)}-{fecha_actual.year}')

                fecha_corte = datetime.today().date() + relativedelta(day=1)
                fecha_corte += relativedelta(months=1)
                paquete = {
                    'tiene_pagos': True,
                    'fecha_actual': fecha_actual,
                    'id_alumno': id_alumno,
                    'fecha_corte': fecha_corte,
                    'cant_meses_abonados': cantidad_meses_abono,
                    'meses_abonados': meses_abono,
                    'cant_meses_adeudados': cantidad_meses_adeudo,
                    'meses_adeudados': meses_adeudo
                }
                # Información de pago recuperada con éxito
                app.logger.info('Información de pago recuperada con éxito')
                return render_template('poner-pagos.html', form=form, paquete=paquete, alumno=alumno)

            else: 
                app.logger.warn('Se encontró un pago, pero no se encontró detalle del mismo')
        else: 
            # Aquí habría que poner que pueda poner el primer pago
            fecha_actual = datetime.now().date()
            fecha_corte = datetime.today().date() + relativedelta(day=1)
            fecha_corte += relativedelta(months=1)
            paquete = {
                'tiene_pagos': False,
                'fecha_actual': fecha_actual,
                'fecha_corte': fecha_corte,
                'id_alumno': id_alumno,
                'cant_meses_abonados': 0,
                'meses_abonados': 0,
                'cant_meses_adeudados': 0,
                'meses_adeudados': 0
            }

            # El alumno no cuenta con ningún pago, ingresa el primer pago
            print('El alumno no cuenta con ningún pago, ingresa el primer pago')
            app.logger.info('El alumno no cuenta con ningún pago, ingresa el primer pago')
            return render_template('poner-pagos.html', form=form, paquete=paquete, alumno=alumno)
        
    # No se pudo conectar a la base de datos
    app.logger.error('Se encontró un pago, pero no se encontró detalle del mismo')
    return render_template('poner-pagos.html', form=form, paquete=paquete, alumno=alumno)

# SDADASDASDA
@app.route('/consulta/no', methods = ['GET', 'POST'])
@login_required
def consultaId():

    alumnos = Alumno.get_all(True, current_user=current_user)
    deudores = []
    for alumno in alumnos:
        query = """
            DECLARE @ID_ultimo_pago INT

            SELECT TOP(1) @ID_ultimo_pago = Pago_alumno.ID_pago_alumno
            FROM Pago_alumno, Historial_abonos, Pagos, Anios_pago
            WHERE Pagos.ID_anio_pago = Anios_pago.ID_anio
                AND Pago_alumno.ID_alumno = ? 
                AND Pago_alumno.Estatus = 1
                AND Pago_alumno.ID_pago_alumno = Historial_abonos.ID_pago_alumno
                AND Pago_alumno.ID_pago = Pagos.ID_pago
            ORDER BY Pagos.ID_anio_pago DESC, 
                    Pagos.ID_mes_pago DESC, 
                    Pagos.ID_dia_pago DESC

            SELECT TOP(1) Pago_alumno.Id_pago_alumno as ID_pago_alumno, Meses_abono.ID_mes, Meses_abono.Mes, Anios_abono.Anio
            FROM Pago_alumno
                JOIN Historial_abonos on Pago_alumno.ID_pago_alumno = Historial_abonos.ID_pago_alumno
                JOIN Anios_abono on Anios_abono.ID_anio = Historial_abonos.ID_anio	
                JOIN Meses_abono on Meses_abono.ID_mes = Historial_abonos.ID_mes
            WHERE Pago_alumno.ID_pago_alumno = @ID_ultimo_pago
            ORDER BY Anios_abono.Anio DESC,
                Historial_abonos.ID_mes DESC
            """
        params = (alumno.id,)
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute(query, params)
            ultimo_mes = cursor.fetchone()
            if ultimo_mes is not None:
                # ver_atributos(ultimo_mes)
                mes = int(ultimo_mes.ID_mes)
                anio = int(ultimo_mes.Anio)
                fecha_actual = datetime.now().date()
                fecha_previa = datetime.strptime(nums_to_str_date(1, mes, anio), '%Y-%m-%d').date()
                # print(fecha_actual)
                # print(fecha_previa)

                if (anio, mes) < (fecha_actual.year, fecha_actual.month):
                    print(f'Último mes pagado: {mes}, Año: {anio}\nMes actual: {fecha_actual.month}, Año actual: {fecha_actual.year}')
                    
                    numero = diferencia_meses(fecha_actual, fecha_previa)

                    print(f'No se ha pagado el periodo actual, debe {numero} meses')
                    setattr(alumno, 'mes', ultimo_mes.Mes)
                    setattr(alumno, 'anio', ultimo_mes.Anio)
                    setattr(alumno, 'meses_adeudados', numero)
                    deudores.append(alumno)
                

    for d in deudores:
        print(d.nombres)
    return render_template('pagos_completos.html', user = current_user, alumnos = deudores)




if __name__ == '__main__':
    app.run(debug=True)
