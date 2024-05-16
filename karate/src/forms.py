from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from datetime import datetime
from wtforms import StringField, SubmitField, PasswordField, EmailField, TelField, DateField
from wtforms.validators import DataRequired, Email, Length, Regexp

class SignUpForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[
                DataRequired(message='Este campo es obligatorio.'),
                Length(min=5, max=20, message='El nombre de usuario debe contener entre 5 y 20 caracteres.'),
                Regexp(regex='(?=.*[a-zA-Z])(^[\\w]{5,20})$', message='El nombre de usuario sólo debe contener letras (sin signos diacríticos), números o guiones bajos, y no debe contener espacios.')])
    password = PasswordField('Contraseña', validators=[
                DataRequired(message='Este campo es obligatorio.'),
                Length(min=8, max=20, message='La contraseña debe contener entre 8 y 20 caracteres.')])
    email = EmailField('Correo electrónico', validators=[
                DataRequired('Este campo es obligatorio.'),
                Email(message='Este correo electrónico no es válido, asegúrate de escribirlo correctamente.', granular_message=False),
                Length(min=3, max=40, message='El correo electrónico ingresado es demasiado largo.')
                ])
    telefono = TelField('Teléfono', validators=[
                DataRequired(message='Este campo es obligatorio'),
                Length(min=10, max=10, message='Ingresa un teléfono válido (10 dígitos, sin guiones)'),
                Regexp(regex='^[0-9]{10}$', message='El teléfono no puede contener letras, espacios, guiones o caracteres especiales.')
                ])
    date = DateField('Fecha de nacimiento', format="%Y-%m-%d", validators=[
                DataRequired(message='Este campo es obligatorio')
                ])
    submit = SubmitField('Registrar')

    date_min = ''
    date_max = ''

    def __init__(self, **kwargs):
        self.date_min = datetime.strptime('2000-01-01', '%Y-%m-%d').date()
        self.date_max = datetime.now().date()
        super(SignUpForm, self).__init__(**kwargs)
