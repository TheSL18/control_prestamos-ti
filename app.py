#!/usr/bin/env python

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
import bcrypt
from datetime import datetime
import configparser

# Leer configuración de la base de datos
config = configparser.ConfigParser()

def cargar_configuracion():
    try:
        config.read('config.ini')
        db_config = {
            'host': config['DATABASE']['host'],
            'port': config['DATABASE']['port'],
            'user': config['DATABASE']['user'],
            'password': config['DATABASE']['password'],
            'database': config['DATABASE']['database']
        }
    except KeyError:
        # Configuración predeterminada si no existe el archivo o alguna clave
        db_config = {
            'host': '127.0.0.1',
            'port': '3306',
            'user': 'root',
            'password': '',
            'database': 'inventario_equipos'
        }
    return db_config

def guardar_configuracion(config_data):
    config['DATABASE'] = config_data
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# Función de conexión a la base de datos
def conectar_db():
    db_config = cargar_configuracion()
    return mysql.connector.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )

# Función para mostrar la ventana de configuración de la base de datos
def mostrar_ventana_configuracion():
    ventana_configuracion = tk.Tk()
    ventana_configuracion.title("Configuración de la Base de Datos")
    ventana_configuracion.geometry("400x300")

    db_config = cargar_configuracion()

    tk.Label(ventana_configuracion, text="Host").pack()
    entrada_host = tk.Entry(ventana_configuracion)
    entrada_host.pack()
    entrada_host.insert(0, db_config['host'])

    tk.Label(ventana_configuracion, text="Puerto").pack()
    entrada_port = tk.Entry(ventana_configuracion)
    entrada_port.pack()
    entrada_port.insert(0, db_config['port'])

    tk.Label(ventana_configuracion, text="Usuario").pack()
    entrada_user = tk.Entry(ventana_configuracion)
    entrada_user.pack()
    entrada_user.insert(0, db_config['user'])

    tk.Label(ventana_configuracion, text="Contraseña").pack()
    entrada_password = tk.Entry(ventana_configuracion, show='*')
    entrada_password.pack()
    entrada_password.insert(0, db_config['password'])

    tk.Label(ventana_configuracion, text="Nombre de la Base de Datos").pack()
    entrada_database = tk.Entry(ventana_configuracion)
    entrada_database.pack()
    entrada_database.insert(0, db_config['database'])

    def guardar_y_cerrar():
        nueva_config = {
            'host': entrada_host.get(),
            'port': entrada_port.get(),
            'user': entrada_user.get(),
            'password': entrada_password.get(),
            'database': entrada_database.get()
        }
        guardar_configuracion(nueva_config)
        messagebox.showinfo("Éxito", "Configuración guardada")
        ventana_configuracion.destroy()

    tk.Button(ventana_configuracion, text="Guardar", command=guardar_y_cerrar).pack()

    ventana_configuracion.mainloop()

# Función de inicio de sesión
def iniciar_sesion():
    usuario = entrada_usuario.get()
    contrasena = entrada_contrasena.get()
    
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE nombre_usuario=%s", (usuario,))
    resultado = cursor.fetchone()
    
    if resultado and bcrypt.checkpw(contrasena.encode(), resultado[2].encode()):
        es_admin = resultado[3]
        messagebox.showinfo("Éxito", "Inicio de sesión correcto")
        ventana_login.destroy()
        mostrar_ventana_principal(es_admin)
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    
    cursor.close()
    conexion.close()

# Función para mostrar la ventana principal
def mostrar_ventana_principal(es_admin):
    ventana_principal = tk.Tk()
    ventana_principal.title("Sistema de Inventario y Préstamo")
    ventana_principal.geometry("1200x600")
    
    # Mostrar inventario
    def mostrar_inventario():
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT equipos.id, equipos.nombre, equipos.descripcion, equipos.tipo, 
                   CASE WHEN equipos.disponible THEN 'Disponible' ELSE 'En préstamo' END AS estado, 
                   equipos.codigo_barras, 
                   COALESCE(usuarios.nombres, '') AS prestado_a, 
                   COALESCE(usuarios.dependencia, '') AS dependencia
            FROM equipos
            LEFT JOIN prestamos ON equipos.id = prestamos.equipo_id AND prestamos.fecha_devolucion IS NULL
            LEFT JOIN usuarios ON prestamos.usuario_id = usuarios.id
        """)
        equipos = cursor.fetchall()
        
        for row in tabla_inventario.get_children():
            tabla_inventario.delete(row)
        
        for equipo in equipos:
            tabla_inventario.insert("", "end", values=equipo)
        
        cursor.close()
        conexion.close()

    # Actualizar el estado del equipo seleccionado
    def actualizar_estado():
        selected_item = tabla_inventario.selection()
        if not selected_item:
            messagebox.showerror("Error", "Debe seleccionar un equipo para actualizar")
            return

        item_values = tabla_inventario.item(selected_item, 'values')
        equipo_id = item_values[0]

        ventana_actualizar_estado = tk.Tk()
        ventana_actualizar_estado.title("Actualizar Estado del Equipo")
        ventana_actualizar_estado.geometry("300x200")

        tk.Label(ventana_actualizar_estado, text=f"Equipo: {item_values[1]}").pack()

        estado_var = tk.StringVar()
        estado_var.set(item_values[4])  # Estado actual

        tk.Label(ventana_actualizar_estado, text="Nuevo Estado").pack()
        opciones_estado = ["Disponible", "En préstamo", "Mantenimiento", "Fuera de servicio"]
        menu_estado = ttk.Combobox(ventana_actualizar_estado, textvariable=estado_var, values=opciones_estado)
        menu_estado.pack()

        def confirmar_cambio_estado():
            nuevo_estado = estado_var.get()
            disponible = nuevo_estado == "Disponible"
            conexion = conectar_db()
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE equipos SET disponible = %s WHERE id = %s",
                (disponible, equipo_id)
            )
            conexion.commit()
            cursor.close()
            conexion.close()

            ventana_actualizar_estado.destroy()
            messagebox.showinfo("Éxito", "Estado actualizado")
            mostrar_inventario()

        tk.Button(ventana_actualizar_estado, text="Actualizar", command=confirmar_cambio_estado).pack()

        ventana_actualizar_estado.mainloop()

    # Función para seleccionar el usuario y realizar el préstamo
    def seleccionar_usuario_para_prestamo(codigo_barras):
        ventana_seleccion_usuario = tk.Tk()
        ventana_seleccion_usuario.title("Seleccionar Usuario")
        ventana_seleccion_usuario.geometry("600x200")

        tk.Label(ventana_seleccion_usuario, text="Selecciona el Usuario").pack()

        lista_usuarios = ttk.Combobox(ventana_seleccion_usuario)
        lista_usuarios.pack()

        # Cargar los usuarios en el combobox
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("SELECT id, nombres FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        conexion.close()

        # Mostrar los nombres de los usuarios en el combobox
        lista_usuarios['values'] = [f"{usuario[0]} - {usuario[1]}" for usuario in usuarios]

        def confirmar_prestamo():
            usuario_seleccionado = lista_usuarios.get()
            if usuario_seleccionado:
                usuario_id = int(usuario_seleccionado.split(" - ")[0])  # Obtener el ID del usuario
                realizar_prestamo(codigo_barras, usuario_id)
                ventana_seleccion_usuario.destroy()
            else:
                messagebox.showerror("Error", "Debes seleccionar un usuario")

        tk.Button(ventana_seleccion_usuario, text="Confirmar Préstamo", command=confirmar_prestamo).pack()

        ventana_seleccion_usuario.mainloop()

    # Realizar préstamo
    def realizar_prestamo(codigo_barras, usuario_id):
        fecha_prestamo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, estado FROM equipos WHERE codigo_barras=%s", (codigo_barras,))
    equipo_info = cursor.fetchone()
    
    if equipo_info:
        equipo_id, estado = equipo_info
        if estado == "Dado de baja":
            messagebox.showerror("Error", "Este equipo está dado de baja y no se puede prestar.")
            return

        cursor.execute(
            "INSERT INTO prestamos (equipo_id, usuario_id, fecha_prestamo) VALUES (%s, %s, %s)",
            (equipo_id, usuario_id, fecha_prestamo)
        )
        cursor.execute(
            "UPDATE equipos SET disponible = FALSE WHERE codigo_barras = %s",
            (codigo_barras,)
        )
        conexion.commit()
        messagebox.showinfo("Éxito", "Préstamo realizado")
        mostrar_inventario()
    else:
        messagebox.showerror("Error", "Equipo no encontrado o código de barras incorrecto")
    
    cursor.close()
    conexion.close()

    # Devolver equipo
    def devolver_equipo():
        codigo_barras = entrada_codigo_barras.get()
        fecha_devolucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("SELECT id FROM equipos WHERE codigo_barras=%s", (codigo_barras,))
        equipo_id = cursor.fetchone()
        
        if equipo_id:
            cursor.execute(
                "UPDATE prestamos SET fecha_devolucion = %s WHERE equipo_id = %s AND fecha_devolucion IS NULL",
                (fecha_devolucion, equipo_id[0])
            )
            cursor.execute(
                "UPDATE equipos SET disponible = TRUE WHERE codigo_barras = %s",
                (codigo_barras,)
            )
            conexion.commit()
            messagebox.showinfo("Éxito", "Equipo devuelto")
            mostrar_inventario()
        else:
            messagebox.showerror("Error", "Equipo no encontrado o código de barras incorrecto")
        
        cursor.close()
        conexion.close()

    tk.Label(ventana_principal, text="Inventario de Equipos").pack()
    columnas = ("ID", "Nombre", "Descripción", "Tipo", "Estado", "Código de Barras", "Prestado A", "Dependencia")
    tabla_inventario = ttk.Treeview(ventana_principal, columns=columnas, show="headings")
    for col in columnas:
        tabla_inventario.heading(col, text=col)
    tabla_inventario.pack()

    tk.Button(ventana_principal, text="Mostrar Inventario", command=mostrar_inventario).pack()
    
    tk.Label(ventana_principal, text="Código de Barras del Equipo").pack()
    entrada_codigo_barras = tk.Entry(ventana_principal)
    entrada_codigo_barras.pack()
    
    # Modificar el botón de realizar préstamo para abrir la ventana de selección de usuario
    tk.Button(ventana_principal, text="Realizar Préstamo", command=lambda: seleccionar_usuario_para_prestamo(entrada_codigo_barras.get())).pack()
    tk.Button(ventana_principal, text="Devolver Equipo", command=devolver_equipo).pack()

    if es_admin:
        # Funcionalidades exclusivas para administrador
        tk.Button(ventana_principal, text="Agregar Equipo", command=agregar_equipo).pack()
        tk.Button(ventana_principal, text="Eliminar Equipo", command=eliminar_equipo).pack()
        tk.Button(ventana_principal, text="Agregar Usuario", command=agregar_usuario).pack()
        
        # Botón para actualizar el estado del equipo
        tk.Button(ventana_principal, text="Actualizar Estado", command=actualizar_estado).pack()

    ventana_principal.mainloop()

# Función para agregar equipo (administrador)
def agregar_equipo():
    def agregar():
        nombre = entrada_nombre.get()
        descripcion = entrada_descripcion.get()
        tipo = entrada_tipo.get()
        codigo_barras = entrada_codigo_barras_agregar.get()
        
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO equipos (nombre, descripcion, tipo, codigo_barras, disponible) VALUES (%s, %s, %s, %s, TRUE)",
            (nombre, descripcion, tipo, codigo_barras)
        )
        conexion.commit()
        cursor.close()
        conexion.close()
        
        ventana_agregar.destroy()
        messagebox.showinfo("Éxito", "Equipo agregado")
        mostrar_inventario()

    ventana_agregar = tk.Tk()
    ventana_agregar.title("Agregar Equipo")
    ventana_agregar.geometry("300x300")
    
    tk.Label(ventana_agregar, text="Nombre").pack()
    entrada_nombre = tk.Entry(ventana_agregar)
    entrada_nombre.pack()
    
    tk.Label(ventana_agregar, text="Descripción").pack()
    entrada_descripcion = tk.Entry(ventana_agregar)
    entrada_descripcion.pack()
    
    tk.Label(ventana_agregar, text="Tipo (Computadora Portátil, Audio, Video)").pack()
    entrada_tipo = tk.Entry(ventana_agregar)
    entrada_tipo.pack()
    
    tk.Label(ventana_agregar, text="Código de Barras").pack()
    entrada_codigo_barras_agregar = tk.Entry(ventana_agregar)
    entrada_codigo_barras_agregar.pack()
    
    tk.Button(ventana_agregar, text="Agregar", command=agregar).pack()

    ventana_agregar.mainloop()

# Función para eliminar equipo (administrador)
def eliminar_equipo():
    def eliminar():
        codigo_barras = entrada_codigo_barras_eliminar.get()
        
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM equipos WHERE codigo_barras = %s", (codigo_barras,))
        conexion.commit()
        cursor.close()
        conexion.close()
        
        ventana_eliminar.destroy()
        messagebox.showinfo("Éxito", "Equipo eliminado")
        mostrar_inventario()

    ventana_eliminar = tk.Tk()
    ventana_eliminar.title("Eliminar Equipo")
    ventana_eliminar.geometry("300x200")
    
    tk.Label(ventana_eliminar, text="Código de Barras").pack()
    entrada_codigo_barras_eliminar = tk.Entry(ventana_eliminar)
    entrada_codigo_barras_eliminar.pack()
    
    tk.Button(ventana_eliminar, text="Eliminar", command=eliminar).pack()

    ventana_eliminar.mainloop()

# Función para agregar usuario (administrador)
def agregar_usuario():
    def agregar():
        nombre_usuario = entrada_nombre_usuario.get()
        contrasena = entrada_contrasena_usuario.get()
        es_admin = var_admin.get()
        
        # Encriptar contraseña
        hashed_contrasena = bcrypt.hashpw(contrasena.encode(), bcrypt.gensalt()).decode()
        
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nombre_usuario, contrasena, es_admin) VALUES (%s, %s, %s)",
            (nombre_usuario, hashed_contrasena, es_admin)
        )
        conexion.commit()
        cursor.close()
        conexion.close()
        
        ventana_agregar_usuario.destroy()
        messagebox.showinfo("Éxito", "Usuario agregado")

    ventana_agregar_usuario = tk.Tk()
    ventana_agregar_usuario.title("Agregar Usuario")
    ventana_agregar_usuario.geometry("300x300")
    
    tk.Label(ventana_agregar_usuario, text="Nombre de Usuario").pack()
    entrada_nombre_usuario = tk.Entry(ventana_agregar_usuario)
    entrada_nombre_usuario.pack()
    
    tk.Label(ventana_agregar_usuario, text="Contraseña").pack()
    entrada_contrasena_usuario = tk.Entry(ventana_agregar_usuario, show='*')
    entrada_contrasena_usuario.pack()
    
    var_admin = tk.BooleanVar()
    tk.Checkbutton(ventana_agregar_usuario, text="Es administrador", variable=var_admin).pack()
    
    tk.Button(ventana_agregar_usuario, text="Agregar", command=agregar).pack()

    ventana_agregar_usuario.mainloop()

# Interfaz de inicio de sesión
ventana_login = tk.Tk()
ventana_login.title("Inicio de Sesión")
ventana_login.geometry("300x200")

# Añadir botón para configuración de la base de datos
tk.Button(ventana_login, text="Configuración de la Base de Datos", command=mostrar_ventana_configuracion).pack()

tk.Label(ventana_login, text="Usuario").pack()
entrada_usuario = tk.Entry(ventana_login)
entrada_usuario.pack()

tk.Label(ventana_login, text="Contraseña").pack()
entrada_contrasena = tk.Entry(ventana_login, show='*')
entrada_contrasena.pack()

tk.Button(ventana_login, text="Iniciar Sesión", command=iniciar_sesion).pack()

ventana_login.mainloop()
