from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, current_user, login_user, logout_user

app = Flask(__name__)
# iniciar el LoginManager
login_manager = LoginManager()
login_manager.init_app(app)




from flask_login import login_required

# cuando se ingresan a rutas que sólo deben tener acceso
# los usuarios loggeados, se redirige a la ruta /login
login_manager.login_view = 'login'

@app.route('/vista_protegida')
@login_required
def vista_protegida():
    return '<h1>Requiere iniciar sesión</h1>'



@login_manager.user_loader
def load_user(user_id : str):
    # Primero hay que recuperar al usuario de la BD (o donde los guardemos)
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE username = ?', (user_id,))

    user = cursor.fetchone()
    if user is not None:
        # si se encuentra el usuario entonces lo convertimos en un objeto del modelo
        user_model = User(user.username, 'correo@gmail.com', user.password, False)
        user_model.setUsername(user.username)
        user_model.setPassword(user.contrasenia)
        return user_model

    return None


@app.route('/mis-cursos/')
@login_required # podemos redirigir al usuario al login
def profile():
    # verificamos que el usuario ha iniciado sesión
    if current_user.is_authenticated:
        # mostramos la página y le pasamos la información del usuario
        return render_template('profile.html', user = current_user)
    
    # podemos hacer algo distinto si es un visitante anónimo (quitar @login_required)
    elif current_user.is_anonymous:
        return redirect(url_for('login'))
    




def create_connection():
    pass

class User():
    pass