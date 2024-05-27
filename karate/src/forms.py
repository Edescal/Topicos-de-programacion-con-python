from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from datetime import datetime, timedelta, date
from wtforms import StringField, SubmitField, PasswordField, EmailField, TelField, DateField, SelectField, HiddenField,DecimalField, SelectMultipleField, IntegerField, FieldList
from wtforms.validators import DataRequired, Email, Length, Regexp, ReadOnly, EqualTo, NumberRange
from wtforms.fields import FormField

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
        Length(min=8, max=20, message='La contraseña debe contener entre 8 y 20 caracteres.'),
        EqualTo('confirm_password', 'Las contraseñas deben coincidir. Asegúrate e confirmar la contraseña correctamente.')
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
        Regexp(regex="^([a-zA-Z\u00C0-\u017F]{2,})([ -]?[a-zA-Z\u00C0-\u017F]{2,})*$",
               message='El apellido solo puede contener letras. Los apellidos compuestos deben ir separados por un guión (-)'),
        Length(min=1, max=20, message='El apellido paterno debe contener como máximo 20 caracteres.')
    ])
    apellido_materno = StringField(label='Segundo apellido', validators=[
        DataRequired('Este campo es obligatorio.'),
        Regexp(regex="^([a-zA-Z\u00C0-\u017F]{2,})([ -]?[a-zA-Z\u00C0-\u017F]{2,})*$",
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
    id_alumno = HiddenField()
    fecha_pago = DateField(label='Fecha del pago', format="%Y-%m-%d",
        validators=[DataRequired(message='Este campo es obligatorio'),
    ])
    fecha_corte = DateField(label='Fecha de vencimiento', format="%Y-%m-%d",
        validators=[DataRequired(message='Este campo es obligatorio'),
    ])
    monto = DecimalField('Monto total', validators=[DataRequired('Este campo es obligatorio'), NumberRange(0, 3600)])
    abono = DecimalField('Total de abono')
    adeudo = DecimalField('Total de adeudo')
    cant_meses_abonados = IntegerField('Meses a abonar', validators=[NumberRange(1, 5, 'Entre 1 y 5 campos')])
    cant_meses_adeudados = IntegerField('Meses adeudados', validators=[NumberRange(0, 5, 'Entre 1 y 5 campos')])
    submit = SubmitField('Validar pago')


class RegistrarAsistenciaForm(FlaskForm):
    id_alumno = HiddenField('ID alumno', validators=[DataRequired('Este campo no puede estar vacío.')])
    fecha_asistencia = DateField(label='Fecha de asistencia a la clase', format="%Y-%m-%d",
                                validators=[DataRequired('Este campo es obligatorio.')],
                                default=datetime.now().date())
    dia_clase = SelectField(label='Dia de la semana', coerce=int, validate_choice=True,
                            choices=[(1,'Lunes'),(2,'Martes'),(3,'Miércoles'),(4,'Jueves'),(5,'Viernes'),(6,'Sábado'),(7,'Domingo')],
                            validators=[DataRequired('Este campo no puede estár vacío.')])
    hora_clase = SelectField(label='Hora de la clase:', coerce=int, validate_choice=True,
                             choices=[(-1,''),(0,'00:00'),(1,'01:00'),(2,'02:00'),(3,'03:00'),(4,'04:00'),(5,'05:00'),(6,'06:00'),(7,'07:00'),(8,'08:00'),
                                      (9,'09:00'),(10,'10:00'),(11,'11:00'),(12,'12:00'),(13,'13:00'),(14,'14:00'),(15,'15:00'),(16,'16:00'),(17,'17:00'),
                                      (18,'18:00'),(19,'19:00'),(20,'20:00'),(21,'21:00'),(22,'22:00'),(23,'23:00'),(24,'24:00')],
                             validators=[DataRequired('Este campo no puede estár vacío.')])
    submit = SubmitField('Registrar asistencia')

