from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():

    if request.method == 'POST':
        datos = {
            'nombre' : request.form['Nombre'],
            'email' : request.form['Email'],
            'mensaje' : request.form['Mensaje'],
            'status' : 'enviado'
        }
        return render_template('contacto.html', form = datos)

    return render_template('contacto.html', form = None)

@app.route('/habilidades')
def portfolio():
    return render_template('habilidades.html')

app.run(debug=True)