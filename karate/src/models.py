from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import create_connection
from datetime import datetime, date
from funciones import calcular_edad
import pyodbc

class User(UserMixin):
    def __init__(self, id, password, email, is_admin=False) -> None:
        self.id = id # username
        self.password_hash = password
        self.email = email
        self.is_admin = is_admin

    def set_email(self, email):
        self.email = email

    def set_password(self, password : str):
        self.password_hash =  generate_password_hash(password)
    
    def check_password(self, password : str):
        return check_password_hash(self.password_hash, password)
    
    def check_is_admin(self):
        return self.is_admin

    # Si la tabla tiene más atributos, o necesitamos funciones, se los añadimos acá
    def set_nombres(self, nombres):
        self.nombres = nombres
    
    def set_apellido_paterno(self, apellido_paterno):
        self.apellido_paterno = apellido_paterno
    
    def set_apellido_materno(self, apellido_materno):
        self.apellido_materno = apellido_materno

    def set_fecha_creacion(self, fecha):
        self.fecha_creacion = fecha

    def set_estatus(self, status):
        self.status = status

    @staticmethod
    def get_user(id : str):
        conn = create_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Users WHERE Username = ?', (id,))

            user = cursor.fetchone()
            if user is not None:
                # si se encuentra el usuario entonces lo convertimos en un objeto del modelo
                user_model = User(user.Username, user.Password, user.Email, False)
                # poner los setters
                user_model.set_nombres(user.Nombres)
                user_model.set_apellido_paterno(user.Ap_pat)
                user_model.set_apellido_materno(user.Ap_mat)
                user_model.set_fecha_creacion(user.Fecha_creacion)
                return user_model
        except pyodbc.Error as e:
            print(f'Error en get_user{id}: {str(e)}')
        finally:
            conn.close()
        # si no encuentra nada, devolver None
        return None
    
    @staticmethod
    def get_all_users():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users')

        users = cursor.fetchall()
        if users is not None:
            all_users = []
            for user in users:
                user_model = User(user.Username, user.Password, user.Email, False)
                # poner los setters
                user_model.set_nombres(user.Nombres)
                user_model.set_apellido_paterno(user.Ap_pat)
                user_model.set_apellido_materno(user.Ap_mat)
                user_model.set_fecha_creacion(user.Fecha_creacion)
                all_users.append(user_model)
                
            return all_users

        # si no encuentra nada, devolver None
        return None

    def __repr__(self):
        return '( User {} | Email {} | Creation {} )'.format(self.id, self.email, self.fecha_creacion)
    

class Alumno():
    def __init__(self, id : int, nombres : str, ap_pat : str, ap_mat : str,
                edad : int, total_asist : int, 
                dia : int, id_mes : int, mes : str, anio : int, 
                id_cinta : int, cinta : str, estatus : str, telefono: str) -> None:
        self.id = int(id)
        self.nombres = nombres
        self.apellido_paterno = ap_pat
        self.apellido_materno = ap_mat
        self.cinta = (int(id_cinta), cinta)
        self.edad = int(edad)
        self.total_asistencias = int(total_asist)
        self.estatus = estatus
        self.telefono = telefono
        self.mes_nacimiento = mes
        str_fecha = f'{ str(dia).zfill(2) }-{ str(id_mes).zfill(2) }-{ str(anio).zfill(4) }'
        str_format = '%d-%m-%Y'
        self.fecha_nacimiento = datetime.strptime(str_fecha, str_format).date()

    def __repr__(self) -> str:
        return '[ID {}|Estatus {}|{}|{}|{}|Teléfono {}|Edad {}|Total asist {}|Cinta {}|Fecha nacimiento {}]'.format(
                  str(self.id).zfill(4), self.estatus, self.nombres, self.apellido_paterno, self.apellido_materno, 
                  self.telefono, self.edad, self.total_asistencias, self.cinta[1], str(self.fecha_nacimiento)
            )
    
    def __eq__(self, value: object) -> bool:
        isAlumno = isinstance(value, self.__class__)
        if not isAlumno:
            return False
        
        if self.id != value.id or self.nombres != value.nombres or \
            self.apellido_paterno != value.apellido_paterno or self.apellido_materno != value.apellido_materno or \
            self.edad != value.edad or self.estatus != value.estatus or self.cinta[0] != value.cinta[0] or \
            self.telefono != value.telefono or self.fecha_nacimiento != value.fecha_nacimiento:
            return False
        return True


    @staticmethod
    def get_by_id(id : int):
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                query = """
                    SELECT ID_alumno, Nombres, Ap_pat, Ap_mat, Edad, Total_asistencias,
                        Dias_nacimiento.Dia, Meses_nacimiento.ID_mes, Meses_nacimiento.Mes, Anios_nacimiento.Anio,
                        Cintas.ID_cinta, Cintas.Color, Estatus.Estatus, Telefonos.Telefono
                    FROM Alumnos
                        JOIN Dias_nacimiento ON Alumnos.ID_dia_nac = Dias_nacimiento.ID_dia
                        JOIN Meses_nacimiento ON Alumnos.ID_mes_nac = Meses_nacimiento.ID_mes
                        JOIN Anios_nacimiento ON Alumnos.ID_anio_nac = Anios_nacimiento.ID_anio
                        JOIN Cintas ON Alumnos.ID_cinta = Cintas.ID_cinta
                        JOIN Telefonos ON Alumnos.ID_alumno = Telefonos.ID_telefono
                        JOIN Estatus ON Alumnos.ID_estatus = Estatus.ID_estatus
                    WHERE Alumnos.ID_alumno = ?
                    """
                params = (id,)
                cursor.execute(query, params)
                result = cursor.fetchone()
                if result is not None:
                    alumno = Alumno(*result)
                    calc_edad = calcular_edad(alumno.fecha_nacimiento)
                    if calc_edad != alumno.edad:
                        query = """
                            UPDATE Alumnos SET Edad = ? WHERE ID_alumno = ?
                            """
                        params = (calc_edad, id)
                        cursor.execute(query, params)
                        cursor.commit()
                    return alumno
            except pyodbc.Error as e: print(f'[ERROR - DB( getUser({id}) )] - [{str(e)}]')
            finally: conn.close()
        return None
    
    @staticmethod
    def get_all(exclude_bajas : bool = True):
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                query = """
                    SELECT ID_alumno, Nombres, Ap_pat, Ap_mat, Edad, Total_asistencias,
                        Dias_nacimiento.Dia, Meses_nacimiento.ID_mes, Meses_nacimiento.Mes, Anios_nacimiento.Anio,
                        Cintas.ID_cinta, Cintas.Color, Estatus.Estatus, Telefonos.Telefono
                    FROM Alumnos
                        JOIN Dias_nacimiento ON Alumnos.ID_dia_nac = Dias_nacimiento.ID_dia
                        JOIN Meses_nacimiento ON Alumnos.ID_mes_nac = Meses_nacimiento.ID_mes
                        JOIN Anios_nacimiento ON Alumnos.ID_anio_nac = Anios_nacimiento.ID_anio
                        JOIN Cintas ON Alumnos.ID_cinta = Cintas.ID_cinta
                        JOIN Telefonos ON Alumnos.ID_alumno = Telefonos.ID_telefono
                        JOIN Estatus ON Alumnos.ID_estatus = Estatus.ID_estatus
                    """
                cursor.execute(query)
                result = cursor.fetchall()
                if result is not None:
                    all_alumnos = []
                    for record in result:
                        alumno = Alumno(*record)
                        if exclude_bajas and alumno.estatus != 'BAJA':
                            all_alumnos.append(alumno)
                        elif not exclude_bajas: all_alumnos.append(alumno)

                    return all_alumnos
            except pyodbc.Error as e: print(f'[ERROR - DB( getUser({id}) )] - [{str(e)}]')
            finally: conn.close()
        return None