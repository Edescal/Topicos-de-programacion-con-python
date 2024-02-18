from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    datosWeb = {
        'titulo' : 'Tópicos de programación con Flask',
        'nombre' : 'Eduardo Escalante'
    }
    return render_template('index.html', data = datosWeb)

# Ruta para mostrar un mensaje personalizado
@app.route('/mensaje/<nombre>')
def mensaje(nombre):
    datosMensaje = {
        "titulo":"Mensaje para "+nombre,
        "nombre": nombre
    }
    return render_template('mensaje.html', data = datosMensaje)


# Ruta que usa el formulario para crear el mensaje personalizado
@app.route('/crearmensaje')
def crearmensaje():
    name = request.args['name'] # lo que se escribió en el nombre
    return redirect(url_for('mensaje', nombre = name)) # redirigir url


# Iniciar la applicación
app.run(debug=True)