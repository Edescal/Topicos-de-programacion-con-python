from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/', methods =['GET', 'POST'])
def index():
    datosWeb = {
        'titulo' : 'Tópicos de programación con Flask',
        'nombre' : 'Eduardo Escalante'
    }

    if request.method == 'POST':
        nombre = request.form['Nombre']
        correo = request.form['Correo']
        psw = request.form.get('Password')
        return render_template('index.html', data = datosWeb, request = request.method, nombre = nombre, correo = correo, password = psw)

    return render_template('index.html', data = datosWeb)

# Ruta para mostrar un mensaje personalizado
@app.route('/mensaje/<nombre>', methods=['GET'])
def mensaje(nombre):
    datosMensaje = {
        "titulo":"Mensaje para "+nombre,
        "user": nombre
    }
    return render_template('mensaje.html', data = datosMensaje)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/about')
def about():
    datos = {
        'titulo':"Sobre esta página"
    }
    return render_template('about.html', data=datos)

# Iniciar la applicación
app.run(debug=True)