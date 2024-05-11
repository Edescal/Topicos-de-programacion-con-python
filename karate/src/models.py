from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

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

    # Si la tabla tiene más atributos, o necesitamos funciones, se los añadimos acá
    def set_nombres(self, nombres):
        self.nombres = nombres
    
    def set_apellido_paterno(self, apellido_paterno):
        self.apellido_paterno = apellido_paterno
    
    def set_apellido_materno(self, apellido_materno):
        self.apellido_materno = apellido_materno

    def set_fecha_creacion(self, fecha):
        self.fecha_creacion = fecha

    def __repr__(self):
        return '<User {}>\n<Email {}>\n<nombres {}>'.format(self.id, self.email, self.nombres)
    
