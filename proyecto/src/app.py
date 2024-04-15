from flask import Flask, render_template, request, redirect, url_for,send_file
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import config, io, os

app = Flask(__name__)

app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
app.config['HEX_SEC_KEY'] = config.HEX_SEC_KEY
app.config['ALLOWED_EXTENSIONS'] = config.ALLOWED_EXTENSIONS

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def registro():
    return render_template('registro.html')






# RUTA PARA SOLICITAR IMÁGENES
@app.route('/api/tests/<int:id>', methods = ['GET', 'POST'])
def test(id):
    if id == 2:
        app.logger.debug('Accediendo a imagen de la DB')

        cur = mysql.connection.cursor()
        cur.execute(f'select imagen, descripcion from pruebas')
        items = cur.fetchone()
        imagen = items[0]
        cur.close()

        return send_file(io.BytesIO(imagen), items[1])

    return render_template('images.html')

# RUTA PARA SUBIR IMÁGENES
@app.route('/api/upload', methods=['GET','POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    
    if request.method == 'POST':
        archivo = request.files['archivo']
        if archivo.filename == '':
            app.logger.error('Se intentó subir un archivo vacío')
            pass
        elif archivo and allowed_file(archivo.filename):
            filename = secure_filename(archivo.filename)    
            mimetype = archivo.mimetype        
            filepath = f'{app.static_folder}\\img\\uploads\\{filename}'

            archivo.save(filepath)
            archivo.stream.seek(0)
            bytes = archivo.stream.read()

            cur = mysql.connection.cursor()
            cur.execute('insert into pruebas (nombre, descripcion, imagen) values (%s, %s, %s)', (filename, mimetype, bytes))
            cur.close()
            mysql.connection.commit()

            if not os.path.exists(filepath):
                app.logger.error(
                    f'Error al guardar imagen: {filename} : {mimetype}\
                    | No se creó el directorio correctamente')
                
            return render_template('images.html', filename = filename)
        
        return render_template('images.html')

# COMPROBAR QUE LA EXTENSIÓN DEL ARCHIVO ES PERMITIDA
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']




# Iniciar la applicación
if __name__ == '__main__':
    app.run(debug=True)
