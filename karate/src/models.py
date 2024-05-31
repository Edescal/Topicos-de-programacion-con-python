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
        if conn is not None:
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
                id_cinta : int, cinta : str, estatus : str, telefono: str, id_user : str) -> None:
        self.id = int(id)
        self.id_user = id_user
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

    def update_status(self):
        if self.estatus == 'BAJA':
            print(f'El alumno {self.nombres} {self.apellido_paterno} fue dado de baja. No se cambiará su estatus.')
            return (f'Estatus actual: {self.estatus} | Deseado: {3}')
    
        conn = create_connection()
        if conn is not None:
            consulta_ultimo_mes_pagado = """
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

                SELECT TOP(1) Pago_alumno.Id_pago_alumno as ID_pago_alumno, Meses_abono.ID_mes, Anios_abono.Anio
                FROM Pago_alumno
                    JOIN Historial_abonos on Pago_alumno.ID_pago_alumno = Historial_abonos.ID_pago_alumno
                    JOIN Anios_abono on Anios_abono.ID_anio = Historial_abonos.ID_anio	
                    JOIN Meses_abono on Meses_abono.ID_mes = Historial_abonos.ID_mes
                WHERE Pago_alumno.ID_pago_alumno = @ID_ultimo_pago
                ORDER BY Anios_abono.Anio DESC,
                    Historial_abonos.ID_mes DESC
                """
            params = (self.id,)
            # print(f'Alumno: {self.nombres} {self.apellido_paterno}')
            try:
                cursor = conn.cursor()
                cursor.execute(consulta_ultimo_mes_pagado, params)
                ultimo_mes = cursor.fetchone()

                def actualizar_status(nuevoEstatus : int):
                    clave = 'ACTIVO' if nuevoEstatus == 1 else 'PENDIENTE'
                    if self.estatus != clave:
                        # print(f'Se debe cambiar su estatus a PENDIENTE (ID = {nuevoEstatus})')
                        self.estatus = clave
                        update_query = f'UPDATE Alumnos SET ID_estatus = {nuevoEstatus} WHERE ID_alumno = ?'
                        try:
                            cursor.execute(update_query, params)
                            cursor.commit()
                            # print('Estatus cambiado con éxito')
                        except pyodbc.DatabaseError as e:
                            # print(f'Error en el UPDATE: {e}')
                            cursor.rollback()
            
                if ultimo_mes is not None:
                    mes = int(ultimo_mes.ID_mes)
                    anio = int(ultimo_mes.Anio)
                    fecha_actual = datetime.now().date()

                    if (anio, mes) < (fecha_actual.year, fecha_actual.month):
                        # print('El periodo actual no está pagado')
                        # print (f'Estatus actual: {self.estatus} | Deseado: {2}')
                        actualizar_status(2)
                        return
                    else:
                        # print('El periodo actual ya está pagado')
                        # print(f'Estatus actual: {self.estatus} | Deseado: {1}')
                        actualizar_status(1)
                        return
                else:
                    # print('No tiene ningún pago validado')
                    # print(f'Estatus actual: {self.estatus} | Deseado: {2}')
                    actualizar_status(2)
                    return

            except pyodbc.DatabaseError as e:
                print(f'Error al intentar actualizar el estatus del alumno: {e}')
                conn.rollback()
            finally: conn. close()
        
        print('No se conectó a la BD')
        return (f'Estatus actual: {self.estatus} | Deseado: {2}')

    @staticmethod
    def get_by_id(id : int, current_user : UserMixin = None):
        conn = create_connection()
        if conn is not None:
            try:
                extra = 'and Alumnos.ID_user = ?' if current_user is not None else ''
                cursor = conn.cursor()
                query = f"""
                    SELECT ID_alumno, Nombres, Ap_pat, Ap_mat, Edad, Total_asistencias,
                        Dias_nacimiento.Dia, Meses_nacimiento.ID_mes, Meses_nacimiento.Mes, Anios_nacimiento.Anio,
                        Cintas.ID_cinta, Cintas.Color, Estatus.Estatus, Telefonos.Telefono, Alumnos.ID_user
                    FROM Alumnos
                        JOIN Dias_nacimiento ON Alumnos.ID_dia_nac = Dias_nacimiento.ID_dia
                        JOIN Meses_nacimiento ON Alumnos.ID_mes_nac = Meses_nacimiento.ID_mes
                        JOIN Anios_nacimiento ON Alumnos.ID_anio_nac = Anios_nacimiento.ID_anio
                        JOIN Cintas ON Alumnos.ID_cinta = Cintas.ID_cinta
                        JOIN Telefonos ON Alumnos.ID_alumno = Telefonos.ID_telefono
                        JOIN Estatus ON Alumnos.ID_estatus = Estatus.ID_estatus
                    WHERE Alumnos.ID_alumno = ? {extra}
                    """
                # params
                if current_user is not None:
                    params = (id, current_user.get_id())
                else: params = (id)

                cursor.execute(query, params)
                result = cursor.fetchone()
                if result is not None:
                    alumno = Alumno(*result)
                    alumno.update_status()
                    # ver si actualizar edad
                    calc_edad = calcular_edad(alumno.fecha_nacimiento)
                    if calc_edad != alumno.edad:
                        alumno.edad = calc_edad
                        query = """
                            UPDATE Alumnos SET Edad = ? WHERE ID_alumno = ?
                            """
                        params = (calc_edad, id)
                        cursor.execute(query, params)
                    
                    # ver si actualizar total asistencias
                    consultar_asistencias = """
                        SELECT COUNT(*)
                        FROM Alumnos JOIN Alumno_clase ON Alumnos.ID_alumno = Alumno_clase.ID_alumno
                        WHERE Alumnos.ID_alumno = ? AND Alumno_clase.Estatus = 1
                        """
                    params = (id)
                    cursor.execute(consultar_asistencias, params)
                    total_asistencias = cursor.fetchone()[0]
                    if total_asistencias != alumno.total_asistencias:
                        alumno.total_asistencias = total_asistencias
                        query = """
                            UPDATE Alumnos SET Total_asistencias = ? WHERE ID_alumno = ?
                            """
                        params = (total_asistencias, id)
                        cursor.execute(query, params)

                    cursor.commit()
                    return alumno
            except pyodbc.Error as e: print(f'[ERROR - DB( getUser({id}) )] - [{str(e)}]')
            finally: conn.close()
        return None
    
    @staticmethod
    def get_all(exclude_bajas : bool = True, current_user : UserMixin = None):
        conn = create_connection()
        if conn is not None:
            try:
                extra = 'WHERE Alumnos.ID_user = ?' if current_user is not None else ''
                cursor = conn.cursor()
                query = f"""
                    SELECT ID_alumno, Nombres, Ap_pat, Ap_mat, Edad, Total_asistencias,
                        Dias_nacimiento.Dia, Meses_nacimiento.ID_mes, Meses_nacimiento.Mes, Anios_nacimiento.Anio,
                        Cintas.ID_cinta, Cintas.Color, Estatus.Estatus, Telefonos.Telefono, Alumnos.ID_user
                    FROM Alumnos
                        JOIN Dias_nacimiento ON Alumnos.ID_dia_nac = Dias_nacimiento.ID_dia
                        JOIN Meses_nacimiento ON Alumnos.ID_mes_nac = Meses_nacimiento.ID_mes
                        JOIN Anios_nacimiento ON Alumnos.ID_anio_nac = Anios_nacimiento.ID_anio
                        JOIN Cintas ON Alumnos.ID_cinta = Cintas.ID_cinta
                        JOIN Telefonos ON Alumnos.ID_alumno = Telefonos.ID_telefono
                        JOIN Estatus ON Alumnos.ID_estatus = Estatus.ID_estatus
                    {extra}
                    """
                # params
                if current_user is not None:
                    params = (current_user.get_id())
                else: params = ()
                
                cursor.execute(query, params)
                result = cursor.fetchall()
                if result is not None:
                    all_alumnos = []
                    for record in result:
                        alumno = Alumno(*record)
                        if alumno is not None:
                            alumno.update_status()
                            if exclude_bajas and alumno.estatus != 'BAJA':
                                all_alumnos.append(alumno)
                            elif not exclude_bajas: 
                                all_alumnos.append(alumno)

                    return all_alumnos
            except pyodbc.Error as e: print(f'[ERROR - DB( getUser({id}) )] - [{str(e)}]')
            finally: conn.close()
        return None
    

