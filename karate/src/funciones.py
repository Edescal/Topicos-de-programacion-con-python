from datetime import datetime

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