import pyodbc
import mariadb

def create_connection():
    try:
        # conn = pyodbc.connect('Driver={SQL Server};'
        #                       'Server=localhost;'
        #                       'Database=Karate;'
        #                       'Trusted_Connection=yes;')
        # return conn
    
        config = {
            'host': '127.0.0.1',
            'port': 3307,
            'user': 'sensei',
            'password': 'doctorpassword',
            'database': 'karate'
        }
        conn = mariadb.connect(**config)
        
        return conn
    except pyodbc.Error as e:
        print(f"Error al conectar a la base de datos: {str(e)}")
        return None
