from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import create_connection
from datetime import datetime

class User(UserMixin):
    def __init__(self, id, password, email, is_admin=False) -> None:
        self.id = id # username
        self.password_hash = generate_password_hash(password)
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

        # si no encuentra nada, devolver None
        return None
    
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
    
