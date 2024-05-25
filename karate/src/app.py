from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, send_from_directory
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from urllib.parse import urlparse
from funciones import calcular_edad, parsear_fecha, ver_atributos, capitalize_each, fetch_all_to_dict_list
from database import create_connection
from datetime import datetime
from models import User, Alumno
from forms import LoginForm, RegistroForm, AlumnoForm, EditarAlumnoForm, ValidarPagoForm, RegistrarAsistenciaForm, SignUpForm
from flask_wtf import CSRFProtect
import config
import pyodbc


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
def Inicio():
    return render_template('Inicio.html',user = current_user)

@app.errorhandler(404)
def page_not_found(e):
    app.logger.error(f'Error en el programa: {str(e)}')
    # Si no existe la pagina vuelve al INICIO
    return redirect(url_for('index'))

@app.route('/favicon.ico') 
def favicon(): 
    #return url_for('static', filename='data:,') # poner esto si no hay favicon.ico
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/index')
def index():
    return render_template('index.html', user = current_user)

#--------------------------------------------------

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
            fecha_nacimiento = form.fecha_nacimiento.data
            edad = calcular_edad(fecha_nacimiento)
            cinturon = form.cinturon.data
            estatus = 1

            id_anio = None
            conn = create_connection()
            if conn is not None:
                try:
                    cursor = conn.cursor()
                    cursor.execute('select ID_anio from Anios_nacimiento where anio = ?', (fecha_nacimiento.year,))
                    id_anio = cursor.fetchone()[0]

                    consultar_telefono = 'select Telefono from Telefonos where Telefono = ?'
                    params = (telefono,)
                    cursor.execute(consultar_telefono, params)
                    telefono_exists = cursor.fetchone()
                    if telefono_exists is not None:
                        flash('El teléfono ya está registrado.', 'error')
                    else:
                        # primero se inserta el teléfono en la BD
                        insertar_telefono = 'insert into Telefonos (Telefono) values (?)'
                        params = (telefono,)
                        cursor.execute(insertar_telefono, params)
                        # luego se inserta el alumno en la BD
                        insertar_alumno = 'insert into Alumnos (Nombres, Ap_pat, Ap_mat, Edad, Total_asistencias, ID_dia_nac, ID_mes_nac, ID_anio_nac, ID_cinta, ID_estatus) values (?,?,?,?,?,?,?,?,?,?)'
                        params = (nombres, apellido_paterno, apellido_materno, edad, 0, fecha_nacimiento.day, fecha_nacimiento.month, id_anio, cinturon, estatus)
                        cursor.execute(insertar_alumno, params)
                        # luego se hace el commit
                        cursor.commit()
                        flash('El alumno fue registrado con éxito.', 'success')

                        print(f'Validado: {(nombres, apellido_paterno, apellido_materno, telefono, edad, 0, fecha_nacimiento.day, fecha_nacimiento.month, id_anio, cinturon, estatus)}')
                except pyodbc.Error as e: print(f"Error al insertar alumno en la base de datos: {str(e)}")
                finally: conn.close()
            pass
        else: print("Esta consulta no fue validada")
    return redirect(url_for('mostrar_todos_los_alumnos'))

@app.route('/alumnos/lista')
@login_required
def mostrar_todos_los_alumnos():
    form = AlumnoForm()
    editForm = EditarAlumnoForm()
    alumnos = Alumno.get_all()
    return render_template('Tabla_Alumnos.html', user = current_user, form = form, editForm = editForm, alumnos = alumnos)

# Método para eliminar un alumno por su ID ---------------------------------------------------------------
@app.route('/eliminar_alumno/<int:id>', methods=['POST'])
@login_required
def eliminar_alumno(id):
    alumno = Alumno.get_by_id(id)
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
                flash(f'Se cambió el estatus del alumno {alumno.nombres} {alumno.apellido_paterno} con ID {id} con éxito', 'success')
            except pyodbc.Error as e: 
                flash('No se pudo cambiar el estatus del alumno', 'error')
                app.logger.error(f"Error al cambiar el estatus del alumno en la base de datos: {str(e)}")
            finally: conn.close()
        else:
            flash('Error al procesar la información', 'error') 
            app.logger.error('Error al conectar a la base de datos')
    else:
        flash(f'Error al eliminar: No se encontró un alumno con el ID {id} en la base de datos', 'error') 
        app.logger.error(f'No se encontró un alumno con el ID {id} en la base de datos.')
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
        fecha_nacimiento = form.fecha_nacimiento.data
        edad = calcular_edad(fecha_nacimiento)
        cinturon = form.cinturon.data
        estatus = form.estatus.data
        id_anio = None

        print(f'Form validado (1/3): {(id_alumno, nombres, apellido_paterno, apellido_materno, telefono, edad, 0, fecha_nacimiento.day, fecha_nacimiento.month, fecha_nacimiento.year, cinturon, estatus)}')
        #estatus_str = 'ACTIVO' if estatus == 1 else 'PENDIENTE' if estatus == 2 else 'BAJA'
        #usuario = Alumno.get_by_id(id_alumno)
        #editado = Alumno(*(id_alumno, nombres, apellido_paterno, apellido_materno, edad, 0, fecha_nacimiento.day, fecha_nacimiento.month, '', fecha_nacimiento.year, cinturon, '', estatus_str, telefono))
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute('select Telefono, Id_telefono from Telefonos where Telefono = ?', (telefono,))
                telefono_exists = cursor.fetchone()
                
                # asegurar que el nuevo telefono no es un duplicado de otro alumno
                es_propio = int(telefono_exists.Id_telefono) == int(id_alumno)
                if telefono_exists is not None and not es_propio: 
                    flash('El teléfono ya está vinculado a otro alumno. No se actualizaron los datos.', 'error')
                else:
                    print(f'Telefono validado (2/3): {(id_alumno, nombres, apellido_paterno, apellido_materno, telefono, edad, 0, fecha_nacimiento.day, fecha_nacimiento.month, id_anio, cinturon, estatus)}')

                    cursor.execute('select ID_anio from Anios_nacimiento where anio = ?', (fecha_nacimiento.year,))
                    id_anio = cursor.fetchone()[0]

                    update_telefono = 'update Telefonos set Telefono = ? where ID_telefono = ?' 
                    params = (telefono, id_alumno)
                    cursor.execute(update_telefono, params)

                    update_alumno = 'update Alumnos set Nombres = ?, Ap_pat = ?, Ap_mat = ?, Edad = ?, ID_dia_nac = ?, ID_mes_nac = ?, ID_anio_nac = ?, ID_cinta = ?, ID_estatus = ? where ID_alumno = ?'
                    params = (nombres, apellido_paterno, apellido_materno, edad, fecha_nacimiento.day, fecha_nacimiento.month, id_anio, cinturon, estatus, id_alumno)
                    cursor.execute(update_alumno, params)

                    cursor.commit()
                    print('Edición completada exitosamente (3/3)')
                    flash(f'Los datos del alumno se actualizaron con éxito.', 'success')
                pass
            except pyodbc.Error as e: print(f'Error: {str(e)}')
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
            return 'Error al conectar a la base de datos'


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
        return redirect(url_for('Inicio')) 

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
                        flash('La contraseña ingresada es incorrecta', 'error')
                        return redirect(url_for('login'))
                    # si user is None, mostrar usuario no encontrado
                    flash('Usuario no encontrado', 'error')
                    return redirect(url_for('login'))
                #
                except pyodbc.Error as e: print(f"Error manipular la base de datos: {str(e)}")
                finally: conn.close()
                #
                flash('Hubo un error al consultar la base de datos. Vuelve a intentarlo.')
                return redirect(url_for('login'))
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

            flash('Hubo un error en el procesamiento del formulario. Vuelve a intentarlo.')
            return redirect(url_for('login'))
            
        # si la conexión falló o hubo una excepción, mostrar error
        flash('Hubo un problema. Vuelve a intentarlo.')
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
                msg = { 'text':'Las contraseñas no coinciden. Asegúrate de confirmar tu contraseña correctamente.' }
                return render_template('register.html', message = msg, form=form) 
            
            password_hash = generate_password_hash(password)
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
                        params = (username, password_hash, email, nombres, apellido_p, apellido_m,)
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
            alumno = Alumno.get_by_id(id)
            if alumno is not None:
                cursor = conn.cursor()
                consulta_pagos = """
                    SELECT Pago_alumno.ID_pago_alumno as id_transaccion,
                        dp.Dia as Dia_pago, mp.Mes as Mes_pago, ap.Anio as Anio_pago, mp.ID_Mes, mp.ID_mes as Mes_pago_ID,
                        Pagos.Monto as Monto_total,
                        Pago_alumno.Abono, Pago_alumno.Adeudo,  
                        Pago_alumno.Meses_abono as Meses_abonados,
                        Pago_alumno.Meses_adeudo as Meses_adeudados,
                        dc.Dia as Dia_corte, mc.Mes as Mes_corte, ac.Anio as Anio_corte, mc.ID_Mes, mc.ID_mes as Mes_corte_ID
                    FROM Pagos
                        JOIN Pago_alumno on Pago_alumno.ID_alumno = Pagos.ID_pago
                        JOIN Alumnos on Alumnos.ID_alumno = Pago_alumno.ID_alumno
                        JOIN Dias_pago dp on Pagos.ID_dia_pago = dp.ID_dia
                        JOIN Dias_pago dc on Pagos.ID_dia_corte = dc.ID_dia
                        JOIN Meses_pago mp on Pagos.ID_mes_pago = mp.ID_mes
                        JOIN Meses_pago mc on Pagos.ID_mes_corte = mc.ID_mes
                        JOIN Anios_pago ap on Pagos.ID_anio_pago = ap.ID_anio
                        JOIN Anios_pago ac on Pagos.ID_anio_corte = ac.ID_anio
                    WHERE Alumnos.ID_alumno = ?
                    """
                params = (id,)
                cursor.execute(consulta_pagos, params)
                resultados = cursor.fetchall()
                info_pagos = None
                asistencias = None
                historial_adeudos = None
                historial_abonos = None
                # consultar todos los pagos en este nivel
                if resultados is not None:
                    info_pagos = []
                    for registro in resultados:
                        info_pagos.append(registro)

                # consultar las asistencias
                consulta_asistencias = """
                SELECT Alumno_clase.ID_alumno_clase as id, 
                    Dias_asist.Dia, Meses_asist.Mes, Anios_asist.Anio, Meses_asist.ID_mes,
                    Dias_semana.Dia as Dia_sem, Horarios.Hora, 
                    Dias_semana.ID_dia_sem as id_dia_sem, Horarios.ID_hora as id_hora
                FROM Alumno_clase, Alumnos, Dias_asist, Meses_asist, 
                    Anios_asist, Clases, Dias_semana, Horarios
                WHERE Alumnos.ID_alumno = Alumno_clase.ID_alumno
                    AND Alumno_clase.ID_dia_asist = Dias_asist.ID_dia
                    AND Alumno_clase.ID_mes_asist = Meses_asist.ID_mes
                    AND Alumno_clase.ID_anio_asist = Anios_asist.ID_anio
                    AND Alumno_clase.ID_clase = Clases.ID_clase
                    AND Clases.ID_dia_semana = Dias_semana.ID_dia_sem
                    AND Clases.ID_hora = Horarios.ID_hora
                    AND Alumnos.ID_alumno = ?
                ORDER BY Anios_asist.Anio DESC, 
                        Meses_asist.ID_mes DESC, 
                        Dias_asist.ID_dia DESC, 
                        Dias_semana.ID_dia_sem DESC, 
                        Horarios.ID_hora 
                OFFSET ? ROWS
                FETCH NEXT ? ROWS ONLY
                """
                # la idea es que en la página se pueda elegir cuántas asistencias mostrar por página
                # los datos se envian en la url como args ,pero tienen valores por defecto si no hay
                page = request.args.get('page', 0)
                elems_per_page = request.args.get('items', 30)
                params = (id,int(page),int(elems_per_page))
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
                return render_template('perfil.html', user = current_user, form=form, pagoForm = pago, asistenciaForm = asist, alumno = alumno, info_pagos=info_pagos, lista_asistencia=asistencias, historial_adeudos=historial_adeudos, historial_abonos=historial_abonos)

            flash(f'No hay un alumno con el id {id} en la base de datos', 'error')
            return redirect(url_for('mostrar_todos_los_alumnos'))
        except pyodbc.Error as e:
            app.logger.error(f"[ERROR EN EL PROGRAMA] Error al ejecutar la consulta: {str(e)}")
            flash(f'Error al recuperar la información del alumnos', 'error')
            return redirect(url_for('mostrar_todos_los_alumnos')) 
        finally:
            conn.close()
    else:
        flash(f'Error al conectar a la base de datos', 'error')
        return redirect(url_for('mostrar_todos_los_alumnos')) 

"""
CONSULTAS DE LOS PAGOS
"""
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
ESTAS FUNCIONES SÓLO SON PARA TESTEAR CÓDIGOS 
DE CUALQUIER COSA QUE QUIERAS PROBAR
"""
from wtforms import StringField, SubmitField, PasswordField, EmailField, TelField, DateField, SelectField, HiddenField,DecimalField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Regexp, ReadOnly
# ----------- ruta para testear funciones nuevas ---------------------

@app.route('/test', methods = ['GET', 'POST'])
def tests():
    # aqui va código que quieras testear
    # nuevas funcionalidades o cosas así
            
    form = ValidarPagoForm()
    if form.validate_on_submit():
        id_alumno = form.id_alumno.data
        fecha_corte = form.fecha_corte.data
        fecha_pago = form.fecha_pago.data
        monto = form.monto.data
        abono = form.abono.data
        adeudo = form.adeudo.data
        cant_meses_abonados = form.cant_meses_abonados.data
        cant_meses_adeudados = form.cant_meses_adeudados.data

        meses_abono = request.form.getlist('meses_abonados[]')
        meses_adeudos = request.form.getlist('meses_adeudados[]')
        

        
        params = (id_alumno, fecha_pago, fecha_corte, monto, abono, adeudo, cant_meses_abonados, meses_abono, cant_meses_adeudados, meses_adeudos)
        print(params)
    else: # Si el formulario no fue validado por algún motivo
        app.logger.info('[Formulario] - [ERROR] - Formulario no validado:')
        if form.errors:
            for error in form.errors:
                app.logger.info(f'[Formulario] - [Error-info] - {error}')
    # array = request.values
    # for value in array:
    #     print((value))


    return render_template('testeando-form-pago.html', form=form)
# ---------------------------------------------------------------------


@app.route('/consulta')
def consulta():
    

    return render_template('testeando_fechas.html', form = form)

@app.route('/consulta/<int:id>', methods = ['GET', 'POST'])
def consultaId(id : int):
    alumno = Alumno.get_by_id(id)
    if alumno is not None:
        app.logger.info(alumno)
    else: app.logger.error(f'No hay alumno con el ID: {id}')

    return render_template('testeo_alumno.html', alumno = alumno)

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
        dia_clase = form.dia_clase.data
        hora_clase = form.hora_clase.data

        app.logger.warning(f'INFORMACIÓN ENVIADA EN LA NUEVA ASISTENCIA: {(id_alumno, fecha_asistencia, dia_clase, hora_clase)}')
        #return redirect(url_for('profile', id=id_alumno))

        #primero verificar que el alumno existe
        alumno_exist = Alumno.get_by_id(id_alumno)
        if alumno_exist is None:
            app.logger.warning('No existe un alumno con la ID ingresada')
            flash('No existe un alumno con la ID ingresada')
            return redirect(url_for('profile', id=id_alumno))

        # primero verificar que exista la clase en la BD
        consulta_clase = """
            SELECT Clases.ID_clase  as id_clase, Dias_semana.Dia as dia_sem, Horarios.hora
            FROM Clases 
                JOIN Dias_semana ON Clases.ID_dia_semana = Dias_semana.ID_dia_sem
                JOIN Horarios ON Clases.ID_hora = Horarios.ID_hora
            WHERE Dias_semana.ID_dia_sem = ?
                AND Horarios.ID_hora = ?
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
                # recuperar la clave foránea del año (servirá después 2000 -> 0; 2024 -> 24)
                id_anio = cursor.execute('SELECT ID_anio as id_anio FROM Anios_asist WHERE Anio = ?', (fecha_asistencia.year,)).fetchone().id_anio

                # aquí habría que ver que no se pueda duplicar una asistencia
                params = (id_alumno, clase.id_clase, fecha_asistencia.day, fecha_asistencia.month, id_anio)
                existe_asistencia = """
                    SELECT ID_alumno, ID_clase, ID_dia_asist, ID_mes_asist, ID_anio_asist 
                    FROM Alumno_clase
                    WHERE ID_alumno = ? and ID_clase = ? and ID_dia_asist = ? and ID_mes_asist = ? and ID_anio_asist = ?
                    """
                cursor.execute(existe_asistencia, params)
                asistencia = cursor.fetchone()
                if asistencia is not None:
                    flash(f'No se permite duplicar asistencias: Ya hay una asistencia registrada de {alumno_exist.nombres} {alumno_exist.apellido_paterno} en la clase del día {clase.dia_sem} {str(fecha_asistencia.day).zfill(2)}/{str(fecha_asistencia.month).zfill(2)}/{fecha_asistencia.year} a las {clase.hora} hrs.', 'error')
                    return redirect(url_for('profile', id=id_alumno))
                    
                # si la clase y el alumno existen, entonces se puede insertar la asistencia
                insertar_asistencia = """
                    INSERT INTO Alumno_clase (ID_alumno, ID_clase, ID_dia_asist, ID_mes_asist, ID_anio_asist)
                    VALUES (?, ?, ?, ?, ?)
                    """
                cursor.execute(insertar_asistencia, params)
                cursor.commit()

                flash(f'Se ha registrado la asistencia del alumno {alumno_exist.nombres} {alumno_exist.apellido_paterno} del {clase.dia_sem} {str(fecha_asistencia.day).zfill(2)}/{str(fecha_asistencia.month).zfill(2)}/{fecha_asistencia.year} a las {clase.hora}', 'success')
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
        app.logger.error(f'No se encontró al alumno con ID={id_alumno}')
        flash(f'No se encontró al alumno con ID={id_alumno}', 'error')
        return redirect(url_for('profile', id=id_alumno)) 
    else:
        #
        conn = create_connection()
        if conn is not None:
            try:
                # vemos si la clase existe y sacamos su id
                consultar_clase = """
                    SELECT Clases.ID_clase as id, Dias_semana.Dia, Horarios.Hora
                    FROM Clases JOIN Dias_semana ON Clases.ID_dia_semana = Dias_semana.ID_dia_sem
                                JOIN Horarios ON Clases.ID_hora = Horarios.ID_hora
                    WHERE Clases.ID_dia_semana = ? AND Clases.ID_hora = ?
                    """
                params = (dia_clase, hora_clase)
                cursor = conn.cursor()
                cursor.execute(consultar_clase, params)
                # vemos si la clase existe en la base de datos
                clase = cursor.fetchone()
                if clase is None:
                    app.logger.error(f'No se encontró la clase del {clase.Dia} a las {clase.Hora} hrs.')
                    flash(f'No se encontró la clase del {clase.Dia} a las {clase.Hora} hrs.', 'error')
                    return redirect(url_for('profile', id=alumno.id)) 
                #
                # si la clase existe
                consultar_asistencia = """
                    SELECT ID_alumno_clase as id, ID_anio_asist as dia, ID_mes_asist as mes, ID_anio_asist as anio
                    FROM Alumno_clase JOIN Anios_asist ON Alumno_clase.ID_anio_asist = Anios_asist.ID_anio
                    WHERE Alumno_clase.ID_alumno = ?
                        AND Alumno_clase.ID_dia_asist = ?
                        AND Alumno_clase.ID_mes_asist = ?
                        AND Anios_asist.Anio = ?
                        AND Alumno_clase.ID_clase = ?
                    """
                params = (alumno.id, fecha_asistencia.day, fecha_asistencia.month, fecha_asistencia.year, clase.id)
                cursor.execute(consultar_asistencia, params)
                asistencia = cursor.fetchone()
                if asistencia is None:
                    app.logger.error(f'No se encontró la asistencia del {clase.Dia} {fecha_asistencia.day} de {fecha_asistencia.month} del {fecha_asistencia.year} a las {clase.Hora} hrs.')
                    flash(f'No se encontró la asistencia de {alumno.nombres} {alumno.apellido_paterno} del {clase.Dia} {str(fecha_asistencia.day).zfill(2)}/{str(fecha_asistencia.month).zfill(2)}/{fecha_asistencia.year} a las {clase.Hora} hrs.', 'error')
                    return redirect(url_for('profile', id=alumno.id)) 
                #
                consulta_eliminar = 'DELETE FROM Alumno_clase WHERE ID_alumno_clase = ?'
                params = (asistencia.id)
                cursor.execute(consulta_eliminar, params)
                cursor.commit()
                app.logger.info(f'Se eliminó la asistencia del {clase.Dia} {fecha_asistencia.day} de {fecha_asistencia.month} del {fecha_asistencia.year} a las {clase.Hora} hrs.')
                flash(f'Se eliminó la asistencia de {alumno.nombres} {alumno.apellido_paterno} del {clase.Dia} {fecha_asistencia.day} de {fecha_asistencia.month} del {fecha_asistencia.year} a las {clase.Hora} hrs.', 'success')
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
    #
    app.logger.error('No se envió una solicitud válida.')
    flash('No se envió una solicitud válida.', 'error')
    return redirect(url_for('profile', id=id_alumno)) 

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
                SELECT Dias_semana.ID_dia_sem as id_dia, Dias_semana.Dia as dia, Horarios.ID_hora as id_hora, Horarios.Hora as hora FROM Clases 
                    INNER JOIN Dias_semana ON Clases.ID_dia_semana = Dias_semana.ID_dia_sem 
                    INNER JOIN Horarios ON Clases.ID_hora = Horarios.ID_hora 
                WHERE UPPER(Dias_semana.ID_dia_sem) = ?
                """
            params = (id_dia,)
            cursor = conn.cursor()
            cursor.execute(consulta, params)
            horarios = cursor.fetchall()
            if horarios is not None:
                horas = fetch_all_to_dict_list(horarios)
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
            select Pago_alumno.Id_pago_alumno, Meses_adeudo.Mes as Nombre_mes, Meses_adeudo.ID_mes as Mes, Anios_adeudo.Anio
            from Alumnos join Pago_alumno on Alumnos.ID_alumno = Pago_alumno.ID_alumno
                join Historial_adeudos on Pago_alumno.ID_pago_alumno = Historial_adeudos.ID_pago_alumnos
                join Meses_adeudo on Meses_adeudo.ID_mes = Historial_adeudos.ID_mes
                join Anios_adeudo on Anios_adeudo.ID_anio = Historial_adeudos.ID_anio	
            where Historial_adeudos.ID_pago_alumnos = ?
            """
            params = (id_pago_alumno,)
            cursor = conn.cursor()
            cursor.execute(query, params)
            historial_adeudo = cursor.fetchall()
            if historial_adeudo is not None:
                historial = fetch_all_to_dict_list(historial_adeudo)
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
                SELECT Pago_alumno.Id_pago_alumno, Meses_abono.Mes as Nombre_mes, Meses_abono.ID_mes as Mes, Anios_abono.Anio
                FROM Alumnos JOIN Pago_alumno on Alumnos.ID_alumno = Pago_alumno.ID_alumno
                    JOIN Historial_abonos on Pago_alumno.ID_pago_alumno = Historial_abonos.ID_pago_alumno
                    JOIN Meses_abono on Meses_abono.ID_mes = Historial_abonos.ID_mes
                    JOIN Anios_abono on Anios_abono.ID_anio = Historial_abonos.ID_anio	
                WHERE Historial_abonos.ID_pago_alumno = ?
                """
            params = (id_pago_alumno,)
            cursor = conn.cursor()
            cursor.execute(consulta_abonos, params)
            historial_abonos = cursor.fetchall()
            if historial_abonos is not None:
                historial = fetch_all_to_dict_list(historial_abonos)
                return jsonify(historial)
            print('QUEEE')
            return jsonify(None)
        except pyodbc.Error as e:
            app.logger.error(f"[ERROR EN EL PROGRAMA] Error al ejecutar la consulta: {str(e)}")
        finally: conn.close()
    return jsonify(None)


if __name__ == '__main__':
    app.run(debug=True)
