from datetime import datetime
import pyodbc
import re

# CALCULA LA EDAD CON LA FECHA DE NACIMIENTO
def calcular_edad(fdn):
    hoy = datetime.today()
    return (hoy.year - fdn.year) - ((hoy.month, hoy.day) < (fdn.month, fdn.day))

def parsear_fecha(fecha):
    return datetime.strptime(fecha, '%Y-%m-%d')

def ver_atributos(row):
    print('Los atributos de esta consulta son:')
    for column in row.cursor_description:
        print(f'¬{column[0]}')

def capitalize_each(input : str):
    # rompe el string en cada palabra
    split = input.strip().split(' ')
    result = []
    for palabra in split:
        # pone en mayúscula y rejunta cada palabra en una lista
        result.append( palabra.capitalize() )
    # vuelve a juntar todo lo de la lista en una sola cadena
    capitalized = ' '.join(palabra for palabra in result if palabra).strip()
    # palabras que son preposiciones y artículos los regresa a lowercase
    preOutput = capitalized.replace(' De ', ' de ').replace(' La ', ' la ')
    def cap(match):
        return match.group(0).upper()
    # capitalizar palabras con guión
    output = re.sub(r'\-[a-z]', cap, preOutput)
    return output

# función ingeniosa para convertir los resultados de un fetchall
# en una lista que puede convertirse a JSON fácilmente
def fetch_all_to_dict_list(fetchall : list):
    list = []
    for record in fetchall:
        dictionary = {}
        for i, column in enumerate(record):
            dictionary.update( {record.cursor_description[i][0] : column} )
        list.append(dictionary)
    return list