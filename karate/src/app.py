from flask import Flask, render_template, request ,redirect
import pyodbc
from database import create_connection

app = Flask(__name__)

conn = create_connection()

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
    nombre = request.form.get('nombre')
    apellido_paterno = request.form.get('apellido_paterno')
    apellido_materno = request.form.get('apellido_materno')
    edad = request.form.get('edad')
    total_asistencias = request.form.get('total_asistencia')
    anio = request.form.get('anio')  
    mes = request.form.get('mes')
    dia = request.form.get('dia')

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

            cursor.execute("INSERT INTO Alumno (Nombre, Apellido_Paterno, Apellido_Materno, Edad, Total_Asistencia, Id_Anio, Id_Mes, Id_Dias) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                           (nombre, apellido_paterno, apellido_materno, edad, total_asistencias, id_anio, id_mes, id_dia))
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
            return render_template('Tabla_Alumnos.html', alumnos=alumnos)
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



#------------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True)
