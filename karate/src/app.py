from flask import Flask, render_template, request ,redirect
import config
import pyodbc
from funciones import calcular_edad, parsear_fecha
from database import create_connection

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config["SESSION_PERMANENT"] = config.SESSION_PERMANENT
app.config["SESSION_TYPE"] = config.SESSION_TYPE


#Direcciones---------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alumno')
def mostrar_formulario():
    return render_template('formulario_agregar_alumno.html')

#--------------------------------------------------

# METODOS PARA AGREGAR ALUMNOS ------------------------------------------------------------------
@app.route('/agregar_alumno', methods=['POST'])
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

            cursor.execute("SELECT ID_Anio FROM Anios_nacimiento WHERE Anio = ?", (anio,))
            result_anio = cursor.fetchone()
            if result_anio:
                id_anio = result_anio[0]
            else:
                cursor.execute("INSERT INTO Anios_nacimiento (Anio) VALUES (?)", (anio,))
                conn.commit()
                id_anio = cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]

            """
            cursor.execute("SELECT ID_Mes FROM Meses_nacimiento WHERE Mes = ?", (mes,))
            result_mes = cursor.fetchone()
            if result_mes:
                id_mes = result_mes[0]
            else:
                cursor.execute("INSERT INTO Meses_nacimiento (Mes) VALUES (?)", (mes,))
                conn.commit()
                id_mes = cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]
            """

            cursor.execute("SELECT ID_Dias FROM Dias_nacimiento WHERE Dias = ?", (dia,))
            result_dia = cursor.fetchone()
            if result_dia:
                id_dia = result_dia[0]
            else:
                cursor.execute("INSERT INTO Dias_nacimiento (Dias) VALUES (?)", (dia,))
                conn.commit()
                id_dia = cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]

            cursor.execute("INSERT INTO Alumnos (Nombres, Ap_pat, Ap_mat, Edad, Total_asistencias, ID_anio_nac, ID_mes_nac, ID_dia_nac, ID_cinta) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (nombre, apellido_paterno, apellido_materno, edad, total_asistencias, id_anio, id_mes, id_dia, id_cinta))
            conn.commit()
            return 'Alumno agregado correctamente'
        except pyodbc.Error as e:
            print(f"Error al insertar alumno en la base de datos: {str(e)}")
            return 'Error al agregar alumno'
        finally:
            conn.close()
    else:
        return 'Error al conectar a la base de datos'

#-------------------------------------------------------------------------------------------------------

# METODO PARA MOSTRAR ALUMNOS----------------------------------------------------------------------------
@app.route('/Tabla_Alumnos')
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

            return render_template('Tabla_Alumnos.html', alumnos = alumnos, cintas = cintas)
        except pyodbc.Error as e:
            print(f"Error al obtener todos los alumnos: {str(e)}")
            return F'Error al obtener los alumnos: {str(e)}'
        finally:
            conn.close()
    else:
        return 'Error al conectar a la base de datos'
#--------------------------------------------------------------------------------------------------------

# Método para eliminar un alumno por su ID -----------------------------------------------------------------------------------------------
@app.route('/eliminar_alumno/<int:id>', methods=['POST'])
def eliminar_alumno(id):
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Alumnos WHERE ID_alumno = ?", (id,))
            conn.commit()
            return redirect('/Tabla_Alumnos') 
        except pyodbc.Error as e:
            print(f"Error al eliminar alumno de la base de datos: {str(e)}")
            return 'Error al eliminar alumno'
        finally:
            conn.close()
    else:
        return 'Error al conectar a la base de datos'

 #--------------------------------------------------------------------------------------------------------

# METODO PARA ACTUALIZAR USUARIO-----------------------------------------------------------------------------------------------
@app.route('/editar_alumno', methods=['POST'])
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('user')
        pswd = request.form.get('password')

        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Users WHERE Username = ? and Password = ?", (user, pswd))
                user = cursor.fetchone()
                if user is not None:
                    print('Inicio de sesión correcto')
                    return redirect('/Tabla_Alumnos') 
                else:
                    print('No existe el usuario')
            except pyodbc.Error as e:
                print(f"Error manipular la base de datos: {str(e)}")
            finally:
                conn.close()

            return render_template('login.html', message = 'ERROR')
        else:
            return 'Error al conectar a la base de datos'
    else:
        return render_template('login.html')
#------------------------------------------------------------------------------------


@app.route('/perfil/alumno/<int:id>', methods = ['GET'])
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
                return render_template('perfil.html', alumno = alumno)
            
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
                return render_template('pagos.html', alumnos = alumnos, mes = mes, ID_mes = id_mes, anio = anio)

        except pyodbc.Error as e:
            app.logger.error(f"[ERROR EN EL PROGRAMA] Error al ejecutar la consulta: {str(e)}")
        finally:
            conn.close()

        return 'Error al recuperar la información del alumno.'
    else:
        return 'Error al conectar a la base de datos'

@app.route('/consultas/pagos/todos', methods = ['GET'])
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
                return render_template('pagos_completos.html', alumnos = alumnos)

        except pyodbc.Error as e:
            app.logger.error(f"[ERROR EN EL PROGRAMA] Error al ejecutar la consulta: {str(e)}")
        finally:
            conn.close()

        return 'Error al recuperar la información del alumno.'
    else:
        return 'Error al conectar a la base de datos'


@app.route('/consultas/pagos/recuperar', methods=['POST'])
def procesar_consulta_pagos():
    if request.form.get('submit') == 'Mostrar todos los registros':
        return redirect('/consultas/pagos/todos')


    consulta = request.form.get('fecha')
    fecha = parsear_fecha(f'{consulta}-01')
    conn = create_connection()
    cursor = conn.cursor()
    mes = cursor.execute('SELECT Mes FROM Meses_nacimiento WHERE ID_mes = ?', (fecha.month,)).fetchone()[0]
    anio = fecha.year
    cursor.close()
    return redirect(f'/consultas/pagos/{mes}/{anio}')

if __name__ == '__main__':
    app.run(debug=True)
