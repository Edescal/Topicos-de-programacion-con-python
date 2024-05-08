from datetime import datetime

# CALCULA LA EDAD CON LA FECHA DE NACIMIENTO
def calcular_edad(fdn):
    hoy = datetime.today()
    return hoy.year - fdn.year - ((hoy.month, hoy.day) < (fdn.month, fdn.day))

def parsear_fecha(fecha):
    return datetime.strptime(fecha, '%Y-%m-%d')