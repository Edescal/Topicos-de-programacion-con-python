import pyodbc

def create_connection():
    try:
        conn = pyodbc.connect('Driver={SQL Server};'
                              'Server=localhost;'
                              'Database=Karate;'
                              'Trusted_Connection=yes;')
        return conn
    except pyodbc.Error as e:
        print(f"Error al conectar a la base de datos: {str(e)}")
        return None
