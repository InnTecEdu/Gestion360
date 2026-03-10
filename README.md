# Gestión360

Aplicación interna para gestión de usuarios y documentos.

## Uso interno

Este repositorio es de uso corporativo. No publicar credenciales, rutas internas ni datos operativos en documentación pública.

## Requisitos

- Python 3.10 o superior
- Acceso a base de datos MySQL corporativa
- Dependencias del archivo requirements.txt

## Instalación

1. Crear y activar entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Crear archivo de entorno:

```bash
cp .env.example .env
```

4. Configurar variables en `.env` (MySQL y Azure).


## Ejecutar proyecto

```bash
python app.py
```

La app inicia en `http://127.0.0.1:5000/`.

## Variables de entorno

Configurar al menos:

- SECRET_KEY
- MYSQL_HOST
- MYSQL_USER
- MYSQL_PASSWORD
- MYSQL_DB

Opcionales para almacenamiento en Azure:

- AZURE_STORAGE_CONNECTION_STRING
- AZURE_STORAGE_CONTAINER
- AZURE_STORAGE_ACCOUNT_URL

## Base de datos

La aplicación utiliza ORM y puede crear tablas faltantes solo cuando DB_AUTO_CREATE=true.

Para producción:

- Definir DB_AUTO_CREATE=false
- Gestionar cambios de esquema mediante migraciones controladas

## Seguridad

- No exponer secretos en repositorio.
- Rotar credenciales si se compartieron por error.
- Mantener permisos mínimos por entorno.


