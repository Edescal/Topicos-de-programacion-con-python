from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from datetime import datetime
from wtforms import StringField, SubmitField, PasswordField, EmailField, TelField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp

# Formulario para testeo /test
class SignUpForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[
                DataRequired(message='Este campo es obligatorio.'),
                Length(min=5, max=20, message='El nombre de usuario debe contener entre 5 y 20 caracteres.'),
                Regexp(regex='^\\S*$', message='El nombre de usuario no debe contener espacios.'),
                Regexp(regex='^.*[a-zA-Z]+.*$ ?', message='El nombre de usuario debe contener al menos una letra (sin signos diacríticos).'),
                Regexp(regex='(?=.*[a-zA-Z])(^[\\w]{0,})$', message='El nombre de usuario sólo debe contener letras (sin signos diacríticos), números o guiones bajos.')
                ])
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

class LoginForm(FlaskForm):
    username = StringField(label='Nombre de usuario', validators=[
        DataRequired(message='Ingresa un nombre de usuario'),
        Length(min=5, max=20, message='El nombre de usuario debe contener entre 5 y 20 caracteres.'),
        Regexp(regex='^\\S*$', message='El nombre de usuario no debe contener espacios.'),
        Regexp(regex='(?=.*[a-zA-Z])(^[\\w]{0,})$', message='El nombre de usuario sólo debe contener letras (sin signos diacríticos), números o guiones bajos.'),
        Regexp(regex='^.*[a-zA-Z]+.*$ ?', message='El nombre de usuario debe contener al menos una letra (sin signos diacríticos).')
    ])
    password = PasswordField(label='Contraseña', validators=[
        DataRequired(message='Ingresa la contraseña'),
        Length(min=8, max=20, message='La contraseña debe contener entre 8 y 20 caracteres')
    ])
    submit = SubmitField('Iniciar sesión')

class RegistroForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[
        DataRequired(message='Este campo es obligatorio.'),
        Length(min=5, max=20, message='El nombre de usuario debe contener entre 5 y 20 caracteres.'),
        Regexp(regex='^\\S*$', message='El nombre de usuario no debe contener espacios.'),
        Regexp(regex='^.*[a-zA-Z]+.*$ ?', message='El nombre de usuario debe contener al menos una letra (sin signos diacríticos).'),
        Regexp(regex='(?=.*[a-zA-Z])(^[\\w]{0,})$', message='El nombre de usuario sólo debe contener letras (sin signos diacríticos), números o guiones bajos.')
    ])
    nombres = StringField('Nombre(s)', validators=[
        DataRequired('Este campo no puede estar vacío.'),
        Regexp(regex="^([a-zA-Z\u00C0-\u017F]{2,})([ -]?[a-zA-Z\u00C0-\u017F]{2,})*$", 
               message="El (los) nombre(s) solo puede(n) contener letras y guiones."),
        Length(min=1, max=40, message='El (los) nombre(s) debe(n) contener como máximo 40 caracteres.')
    ])
    apellido_paterno = StringField('Primer apellido', validators=[
        DataRequired('Este campo no puede estar vacío.'),
        Regexp(regex="^([a-zA-Z\u00C0-\u017F]{2,})([ -]?[a-zA-Z\u00C0-\u017F]{2,})*$",
               message='El apellido solo puede contener letras y guiones.'),
        Length(min=1, max=20, message='El apellido paterno debe contener como máximo 25 caracteres.')
    ])
    apellido_materno = StringField('Segundo apellido', validators=[
        DataRequired('Este campo no puede estar vacío.'),
        Regexp(regex="^([a-zA-Z\u00C0-\u017F]{2,})([ -]?[a-zA-Z\u00C0-\u017F]{2,})*$",
               message='El apellido solo puede contener letras y guiones.'),
        Length(min=1, max=20, message='El apellido materno debe contener como máximo 25 caracteres.')
    ])
    email = EmailField('Correo electrónico', validators=[
        DataRequired('Este campo es obligatorio.'),
        #Regexp(regex='^\\d*$', message='Eres una puta.'),
        Email(message='Este correo electrónico no es válido, asegúrate de escribirlo correctamente.', granular_message=False),
        Length(min=3, max=40, message='El correo electrónico ingresado es demasiado largo.')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='Este campo es obligatorio.'),
        #Regexp(regex='^\\S*$', message='La contraseña no debe contener espacios.'),
        #Regexp(regex='^\\S*$', message='La contraseña debe tener al menos una letra, un número y un caracter especial.'),
        Length(min=8, max=20, message='La contraseña debe contener entre 8 y 20 caracteres.')
    ])
    confirm_password = PasswordField('Confirmar contraseña', validators=[
        DataRequired(message='Este campo es obligatorio.'),
        Length(min=8, max=20, message='La contraseña debe contener entre 8 y 20 caracteres.')
    ])
    submit = SubmitField('Completar registro')

class AlumnoForm(FlaskForm):
    nombres = StringField(label='Nombre(s)', validators=[
        DataRequired('Este campo es obligatorio.'),
        Length(min=1, max=50, message='El (los) nombre(s) debe(n) contener como máximo 50 caracteres.')
    ])
    apellido_paterno = StringField(label='Primer apellido', validators=[
        DataRequired('Este campo es obligatorio.'),
        Length(min=1, max=50, message='El apellido paterno debe contener como máximo 25 caracteres.')
    ])
    apellido_materno = StringField(label='Segundo apellido', validators=[
        DataRequired('Este campo es obligatorio.'),
        Length(min=1, max=50, message='El apellido materno debe contener como máximo 25 caracteres.')
    ])
    telefono = TelField(label='Teléfono', validators=[
        DataRequired(message='Este campo es obligatorio'),
        Length(min=10, max=10, message='Ingresa un teléfono válido (10 dígitos, sin guiones o espacios)'),
        Regexp(regex='^[0-9]{10}$', message='El teléfono no puede contener letras, espacios, guiones o caracteres especiales.')
    ])
    fecha_nacimiento = DateField(label='Fecha de nacimiento', format="%Y-%m-%d", validators=[
        DataRequired(message='Este campo es obligatorio')
    ])
    cinturon = SelectField(label='Cinturón', choices=([(1, 'Blanco'), (2, 'Amarillo'), (3, 'Naranja'),(4, 'Morado'),(5, 'Azúl'),(6, 'Verde'), (7, 'Café'), (8, 'Rojo'), (9, 'Negro')]),
        format="%Y-%m-%d", validators=[
        DataRequired(message='Este campo es obligatorio')
    ])
    submit = SubmitField('Registrar alumno')
    pass