#  Proyecto Encuestas

Sistema de **encuestas e incidencias** desarrollado con **Django + PostgreSQL**, que permite gestionar usuarios, roles y diferentes módulos de organización.

##  Funcionalidades principales
- **Autenticación y Roles**: Administrador, Dirección, Departamento, Jefe de Cuadrilla, Territorial.
- **Gestión de Usuarios (core/)**:
  - Listar usuarios con buscador.
  - Crear, editar, ver detalle y eliminar usuarios.
  - Roles y permisos aplicados con decoradores (`@solo_admin`).
- **Encuestas (`encuestas_app/`)**: Crear encuestas con preguntas y registrar respuestas.
- **Incidencias (`incidencias/`)**: Registrar incidencias, asignarlas a cuadrillas y hacer seguimiento.
- **Organización (`organizacion/`)**: Dirección y Departamento.
- **Territorial (`territorial_app/`)**: Asignación de incidencias por zona.
- **Autenticación extendida (`registration/`)**:
  - Login / Logout.
  - Recuperación y cambio de contraseña vía correo (Gmail).
  - Edición de perfil y registro de usuarios.
- **Templates unificados**: Navbar dinámico, mensajes de estado y layout común en `main_base.html`.

##  Estructura del Proyecto
- `core/` → Gestión de usuarios y vistas principales.
- `organizacion/` → Módulo de Dirección y Departamento.
- `encuestas_app/` → Módulo de encuestas.
- `incidencias/` → Módulo de incidencias.
- `territorial_app/` → Gestión territorial.
- `registration/` → Formularios y vistas de autenticación extendida.
- `encuestas/` → Configuración principal del proyecto (settings, urls, wsgi/asgi).
- `templates/` → Plantillas globales (`main_base.html`, `registration/`, `core/`, etc.).

##  Instalación rápida

```bash
# Crear entorno virtual con Anaconda
conda create -n encuestas_env python==3.11
conda activate encuestas_env

# Instalar dependencias
pip install -r requirements.txt

# Migrar la base de datos
python manage.py migrate

# Crear superusuario (si aún no existe)
python manage.py createsuperuser

# Ejecutar servidor de desarrollo
python manage.py runserver
