import mysql.connector
import bcrypt

def crear_usuario_admin():
    nombre_usuario = "cal"
    contrasena_plana = "caluniminuto80"  # Cambia esta contraseña a una más segura antes de desplegar
    contrasena_hasheada = bcrypt.hashpw(contrasena_plana.encode(), bcrypt.gensalt()).decode()

    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Peloconcha3",
        database="inventario_equipos"
    )
    
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nombre_usuario, contrasena, es_admin) VALUES (%s, %s, %s)",
        (nombre_usuario, contrasena_hasheada, True)
    )
    conexion.commit()
    cursor.close()
    conexion.close()

    print("Usuario administrador creado.")

crear_usuario_admin()

