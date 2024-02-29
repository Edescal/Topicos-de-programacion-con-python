from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/about')
def sobreMi():
    return render_template('info.html')

@app.route('/habilidades')
def portfolio():
    return render_template('habilidades.html')

app.run(debug=True)