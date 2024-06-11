# Sistema de Inventario y Préstamo de Equipos

Este proyecto es una aplicación de escritorio para gestionar el inventario y el préstamo de equipos en una organización. Está desarrollado en Python usando la biblioteca Tkinter para la interfaz gráfica y MySQL como base de datos.

## Características

- **Inicio de sesión**: Autenticación de usuarios con roles (administrador o usuario regular).
- **Gestión de inventario**: Visualización, adición y eliminación de equipos.
- **Préstamos**: Gestión de préstamos y devoluciones de equipos.
- **Actualización de estado**: Modificación del estado de los equipos (disponible, en préstamo, en mantenimiento, fuera de servicio).
- **Configuración de base de datos**: Ventana de configuración para los parámetros de la conexión a la base de datos MySQL.
- **Integridad del código**: Uso de GPG para firmar el archivo `app.py` y verificar su integridad.

## Requisitos

- Python 3.12
- Tkinter
- MySQL
- Paquetes de Python:
  - `mysql-connector-python`
  - `bcrypt`

## Instalación

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/TheSL18/control_prestamos-ti.git
cd control_prestamos-ti
```

### Paso 2: Crear un entorno virtual (opcional pero recomendado)

```bash
python -m venv venv
source venv/bin/activate # En Windows usa `venv\Scripts\activate`
```

### Paso 3: Instalar las dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar la base de datos

```sql
CREATE DATABASE inventario_equipos;

USE inventario_equipos;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) NOT NULL,
    contrasena_hash VARCHAR(100) NOT NULL,
    es_admin BOOLEAN DEFAULT FALSE,
    nombres VARCHAR(100),
    dependencia VARCHAR(100)
);

CREATE TABLE equipos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(50),
    disponible BOOLEAN DEFAULT TRUE,
    codigo_barras VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE prestamos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipo_id INT NOT NULL,
    usuario_id INT NOT NULL,
    fecha_prestamo DATETIME NOT NULL,
    fecha_devolucion DATETIME,
    FOREIGN KEY (equipo_id) REFERENCES equipos(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
```

### Paso 5: Configurar la conexión a la base de datos

Crea un archivo config.ini en el directorio del proyecto con la siguiente estructura y ajusta los valores según tu configuración de MySQL:

```ini
[DATABASE]
host = 127.0.1.1
port = 3306
user = tu_usuario
password = tu_contraseña
database = inventario_equipos
```

### Paso 6: Verificar la integridad del archivo `app.py`

Si el archivo app.py ha sido firmado con GPG, verifica su integridad de la siguiente manera:

1. Importar la clave pública del firmante (si no lo has hecho):
```bash
gpg --keyserver hkps://keys.openpgp.org --recv-keys 3CA0B9DF1BE7CE09
```

2. Verificar la firma del archivo `app.py`:
```bash
gpg --verify app.py.sig app.py
```
Si la verificación es exitosa, podrás proceder con confianza en que el archivo no ha sido alterado.

### Paso 7: Ejecutar la aplicación

```bash
python app.py
```

## Licencia

Licencia
Este proyecto está bajo una Licencia custom. Consulta el archivo [LICENSE](/LICENSE.txt) para más detalles.

## Contacto

Para preguntas o soporte, por favor contacta a kevin.munoz.m@uniminuto.edu o abre un issue en GitHub.

El desarrollador usa llaves [GPG](https://keys.openpgp.org/vks/v1/by-fingerprint/2B9D22B41F2AF1042BFCE73A3CA0B9DF1BE7CE09) para cifrar, firmar o verificar la integridad de los mensajes y para evitar la suplantación de identidad.
