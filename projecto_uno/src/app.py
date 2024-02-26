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
        "user": nombre
    }
    return render_template('mensaje.html', data = datosMensaje)


# Ruta que usa el formulario para procesar y crear el mensaje personalizado
@app.route('/crearmensaje')
def crearmensaje():
    # lo que se escribió en el nombre
    name = request.args['user'] if len(request.args['user']) > 0 else 'visitante'
    return redirect(url_for('mensaje', nombre = name)) # redirigir url


@app.route('/about')
def about():
    datos = {
        'titulo':"Sobre esta página"
    }
    return render_template('about.html', data=datos)

# Iniciar la applicación
app.run(debug=True)