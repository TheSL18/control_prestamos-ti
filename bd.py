import pandas as pd
import mysql.connector
from mysql.connector import Error

# Función para conectar con la base de datos
def conectar_db():
    try:
        conexion = mysql.connector.connect(
            host='127.0.0.1',  # Cambia esto a la dirección de tu servidor de base de datos
            user='root',       # Cambia esto a tu usuario de MariaDB
            password='Peloconcha3', # Cambia esto a tu contraseña de MariaDB
            database='inventario_equipos'  # Cambia esto al nombre de tu base de datos
        )
        if conexion.is_connected():
            print("Conexión exitosa a la base de datos")
            return conexion
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

# Función para cerrar la conexión a la base de datos
def cerrar_db(conexion):
    if conexion.is_connected():
        conexion.close()
        print("Conexión cerrada")

# Función para cargar datos de usuarios desde un archivo Excel y agregarlos a la base de datos
def cargar_usuarios_excel(ruta):
    try:
        # Leer el archivo Excel
        df = pd.read_excel(ruta)
        
        # Conectar a la base de datos
        conexion = conectar_db()
        if not conexion:
            return
        
        cursor = conexion.cursor()
        
        # Crear la tabla de usuarios si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombres VARCHAR(255),
                correo_institucional VARCHAR(255),
                celular VARCHAR(20),
                numero_identificacion VARCHAR(50) UNIQUE,
                dependencia VARCHAR(255)
            ) AUTO_INCREMENT=2
        """)
        
        # Insertar datos en la tabla usuarios
        for index, row in df.iterrows():
            try:
                # Verificar si el valor no es NaN
                if pd.notna(row['Numero de ID']):
                    cursor.execute(
                        "INSERT INTO usuarios (nombres, correo_institucional, celular, numero_identificacion, dependencia) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE nombres=nombres",
                        (row['Nombre'], row['Correo_Institucional'], str(row['Celular']), str(row['Numero de ID']), row['RESP-200-0182'])
                    )
                    print(f"Usuario {row['Nombre']} insertado correctamente")
                else:
                    print("El valor de 'Numero de ID' es NaN. No se puede realizar la inserción.")
            except Error as e:
                print(f"Error al trabajar con la base de datos: {e}")
        
        # Confirmar los cambios
        conexion.commit()
        print("Datos de usuarios agregados exitosamente")
    
    except Error as e:
        print(f"Error al trabajar con la base de datos: {e}")
    
    finally:
        cerrar_db(conexion)

# Ruta al archivo Excel (Cambia esto a la ruta de tu archivo)
ruta_excel = '~/Descargas/PRESTAMOS RECURSOS MOVILES_2024marzo.xlsx'

# Cargar usuarios desde el archivo Excel
cargar_usuarios_excel(ruta_excel)


