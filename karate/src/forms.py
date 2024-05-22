from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from datetime import datetime, timedelta, date
from wtforms import StringField, SubmitField, PasswordField, EmailField, TelField, DateField, SelectField, HiddenField,DecimalField, SelectMultipleField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Regexp, ReadOnly

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
    date = DateField('Fecha de la clase', format="%Y-%m-%d", validators=[
                DataRequired(message='Este campo es obligatorio')
                ])
    submit = SubmitField('Registrar')

    date_min = None
    date_max = None

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
        Length(min=1, max=20, message='El apellido paterno debe contener como máximo 20 caracteres.')
    ])
    apellido_materno = StringField('Segundo apellido', validators=[
        DataRequired('Este campo no puede estar vacío.'),
        Regexp(regex="^([a-zA-Z\u00C0-\u017F]{2,})([ -]?[a-zA-Z\u00C0-\u017F]{2,})*$",
               message='El apellido solo puede contener letras y guiones.'),
        Length(min=1, max=20, message='El apellido materno debe contener como máximo 20 caracteres.')
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
        Regexp(regex="^([a-zA-Z\u00C0-\u017F]{2,})([ ]?[a-zA-Z\u00C0-\u017F]{2,})*$", 
               message="El (los) nombre(s) solo puede(n) contener letras y guiones."),
        Length(min=1, max=40, message='El (los) nombre(s) debe(n) contener como máximo 50 caracteres.')
    ])
    apellido_paterno = StringField(label='Primer apellido', validators=[
        DataRequired('Este campo es obligatorio.'),
        Regexp(regex="^([a-zA-Z\u00C0-\u017F]{2,})([-]?[a-zA-Z\u00C0-\u017F]{2,})*$",
               message='El apellido solo puede contener letras. Los apellidos compuestos deben ir separados por un guión (-)'),
        Length(min=1, max=20, message='El apellido paterno debe contener como máximo 20 caracteres.')
    ])
    apellido_materno = StringField(label='Segundo apellido', validators=[
        DataRequired('Este campo es obligatorio.'),
        Regexp(regex="^([a-zA-Z\u00C0-\u017F]{2,})([-]?[a-zA-Z\u00C0-\u017F]{2,})*$",
               message='El apellido solo puede contener letras. Los apellidos compuestos deben ir separados por un guión (-)'),
        Length(min=1, max=20, message='El apellido paterno debe contener como máximo 20 caracteres.')
    ])
    telefono = TelField(label='Teléfono', validators=[
        DataRequired(message='Este campo es obligatorio'),
        Length(min=10, max=10, message='Ingresa un teléfono válido (10 dígitos, sin guiones o espacios)'),
        Regexp(regex='^[0-9]{10}$', message='El teléfono no puede contener letras, espacios, guiones o caracteres especiales.')
    ])
    fecha_nacimiento = DateField(label='Fecha de nacimiento', format="%Y-%m-%d", default=datetime.now().date() - timedelta(days=365.5 * 3),
        validators=[
        DataRequired(message='Este campo es obligatorio')
    ])
    cinturon = SelectField(label='Cinturón', coerce=int,
        choices=[(1, 'Blanco'), (2, 'Amarillo'), (3, 'Naranja'),(4, 'Morado'),(5, 'Azúl'),(6, 'Verde'), (7, 'Café'), (8, 'Rojo'), (9, 'Negro')],
        validate_choice=True, validators=[DataRequired(message='Este campo es obligatorio')])
    submit = SubmitField('Registrar alumno')
    date_min = datetime.strptime('2000-01-01', '%Y-%m-%d').date()
    date_max = datetime.now().date() - timedelta(days=365.5 * 3)

    def __init__(self, **kwargs):
        super(AlumnoForm, self).__init__(**kwargs)
        self.date_min = datetime.strptime('2000-01-01', '%Y-%m-%d').date()
        self.date_max = datetime.now().date() - timedelta(days=365.5 * 3)

class EditarAlumnoForm(AlumnoForm):
    estatus = SelectField(label='Cambiar estatus', coerce=int, validate_choice=True,
                          choices=[(1, 'ACTIVO'), (2, 'PENDIENTE'), (3, 'BAJA')],
                          validators=[DataRequired('Este campo es obligatorio')])
    id_alumno = HiddenField('ID alumno', validators=[DataRequired('Este campo no puede estar vacío.')])
    pass

class ValidarPagoForm(FlaskForm):
    fecha_corte = DateField(label='Fecha de corte del pago', format="%Y-%m-%d",
        validators=[DataRequired(message='Este campo es obligatorio'),
    ])
    abono = DecimalField('Cantidad a abonar')
    adeudo = DecimalField('Cantidad que debes')
    meses_abono = SelectMultipleField('Meses que se van a abono', validate_choice=True,
        choices=[(1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'),(4, 'Abril'),(5, 'Mayo'),(6, 'Junio'), (7, 'Julio'), (8, 'Agosto'), (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')],
        )
    meses_adeudo = SelectMultipleField('Meses que se van a saldar', validate_choice=True,
        choices=[(1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'),(4, 'Abril'),(5, 'Mayo'),(6, 'Junio'), (7, 'Julio'), (8, 'Agosto'), (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')],
        )
    monto = DecimalField('Monto total', validators=[
        DataRequired('Este campo es obligatorio'), ReadOnly(), Length(min=0, max=360)
    ])
    id_alumno = IntegerField()
    submit = SubmitField('Validar pago')

