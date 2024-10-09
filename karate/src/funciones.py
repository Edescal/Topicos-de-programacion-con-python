from datetime import datetime
import pyodbc
import re

# CALCULA LA EDAD CON LA FECHA DE NACIMIENTO
def calcular_edad(fdn):
    hoy = datetime.today()
    return (hoy.year - fdn.year) - ((hoy.month, hoy.day) < (fdn.month, fdn.day))

def parsear_fecha(fecha : str):
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
    preOutput = capitalized.replace(' De ', ' de ').replace(' DE ', ' de ').replace(' La ', ' la ').replace(' LA ', ' la ')
    def cap(match):
        return match.group(0).upper()
    # capitalizar palabras con guión
    output = re.sub(r'\-[a-z]', cap, preOutput)
    return output

# función ingeniosa para convertir los resultados de un fetchall
# en una lista que puede convertirse a JSON fácilmente
def fetch_all_to_dict_list(fetchall_result : list, cursor):
    list = []
    for record in fetchall_result:
        dictionary = {}
        for i, column in enumerate(record):
            dictionary.update( {cursor.description[i][0] : column} )
        list.append(dictionary)

    return list

def nums_to_str_date(dia, mes, anio):
    return f'{str(anio)}-{str(mes).zfill(2)}-{str(dia).zfill(2)}'

def diferencia_meses(fecha_1, fecha_2) -> int:
    return (fecha_1.year - fecha_2.year) * 12 + fecha_1.month - fecha_2.month
                
def nombre_mes(mes : int):
    if mes == 1:
        return 'enero'
    elif mes == 2:
        return 'febrero'
    elif mes == 3:
        return 'marzo'
    elif mes == 4:
        return 'abril'
    elif mes == 5:
        return 'mayo'
    elif mes == 6:
        return 'junio'
    elif mes == 7:
        return 'julio'
    elif mes == 8:
        return 'agosto'
    elif mes == 9:
        return 'septiembre'
    elif mes == 10:
        return 'octubre'
    elif mes == 11:
        return 'noviembre'
    elif mes == 12:
        return 'diciembre'
    