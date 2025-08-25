# Data Engineering Coding Challenge

Este proyecto es una API RESTful desarrollada con Flask y SQLAlchemy para gestionar información de empleados, departamentos y trabajos, conectada a una base de datos PostgreSQL. 
Incluye endpoints para healthcheck, inserción masiva de datos desde CSV y consultas analíticas.

---

## Requisitos

- Docker
- (Opcional) Python 3.10+ y pip, si deseas correrlo sin Docker
- Acceso a una base de datos PostgreSQL (Railway, Render, etc.)

---

## Instalación y Ejecución con Docker

1. **Clona el repositorio:**

   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd de_coding_challenge2
   ```

2. **Configura las variables de entorno (opcional):**

   Si necesitas cambiar la cadena de conexión a la base de datos, edítala en `app.py`:

   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:contraseña@host:puerto/nombre_db'
   ```

3. **Construye la imagen de Docker:**

   ```bash
   docker build -t de_coding_challenge2 .
   ```

4. **Ejecuta el contenedor:**

   ```bash
   docker run -p 8000:8000 de_coding_challenge2
   ```

   La API estará disponible en [http://localhost:8000](http://localhost:8000)

---

## Instalación y Ejecución Local (sin Docker)

1. **Instala las dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecuta la aplicación:**

   ```bash
   python app.py
   ```

   Por defecto, Flask corre en el puerto 5000.

---

## Endpoints Principales

- `GET /db_health`  
  Verifica la conexión con la base de datos.

- `POST /data/insert`  
  Inserta datos masivos desde archivos CSV ubicados en la carpeta `upload/`.

- `GET /employees-by-quarter`  
  Devuelve el número de empleados contratados por trabajo y departamento en 2021, dividido por trimestre.

- `GET /departments-above-mean`  
  Devuelve los departamentos con contrataciones por encima del promedio en 2021.

---

## Pruebas Automatizadas

Las pruebas están en `test_app.py` y usan `pytest`.

Para ejecutarlas localmente:

```bash
pytest
```

---

## Despliegue en la Nube

Puedes desplegar esta aplicación en cualquier proveedor cloud que soporte Docker (Railway, Render, AWS, GCP, Azure, etc.).

---

## Notas

- Asegúrate de que la base de datos esté accesible desde el contenedor.
- Los archivos CSV deben estar en la carpeta `upload/` para la inserción masiva.

---

## Autor