from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    datosWeb = {
        'titulo' : 'Tópicos de programación con Flask',
        'nombre' : 'Eduardo Escalante'
    }
    return render_template('index.html', data = datosWeb)

# Iniciar la applicación
app.run(debug=True)