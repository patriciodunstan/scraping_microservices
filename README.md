# Proyecto de Microservicios para Scraping de Estados Financieros

Este proyecto implementa una arquitectura de microservicios para realizar scraping de estados financieros de múltiples empresas. Cada empresa puede tener una estructura HTML diferente, y el sistema está diseñado para ser escalable y permitir configuraciones específicas para cada sitio web.

## Tabla de Contenidos

- [Descripción del Proyecto](#descripción-del-proyecto)
- [Arquitectura](#arquitectura)
- [Requisitos Previos](#requisitos-previos)
- [Configuración del Proyecto](#configuración-del-proyecto)
- [Instrucciones para Levantar el Proyecto](#instrucciones-para-levantar-el-proyecto)
- [Uso del Servicio de Scraping](#uso-del-servicio-de-scraping)
- [Ejemplo de Respuesta](#ejemplo-de-respuesta)
- [Problemas Comunes](#problemas-comunes)
- [Contribuciones](#contribuciones)

## Descripción del Proyecto

Este proyecto realiza scraping de estados financieros desde diferentes páginas web usando Selenium y FastAPI. La información se persiste en una base de datos PostgreSQL y se expone a través de una API RESTful para su consumo por otros servicios o aplicaciones frontend.

## Arquitectura

La arquitectura del proyecto está basada en microservicios:

1. **Servicio de Scraping**: Realiza el scraping de los datos financieros utilizando Selenium.
2. **Servicio de Procesamiento**: Estandariza los datos y los prepara para la persistencia.
3. **Servicio de API**: Exposición de los datos financieros a través de una API REST.
4. **Base de Datos**: PostgreSQL para almacenar la información financiera.

## Requisitos Previos

Asegúrate de tener instaladas las siguientes herramientas:

- **Docker** y **Docker Compose** para contenerización de los servicios.
- **Git** para clonar el repositorio.
- **Python 3.9+** si deseas probar el código sin Docker.

## Configuración del Proyecto

1. **Clona el repositorio**:

   ```bash
   git clone https://github.com/tuusuario/scraping_microservices.git
   cd scraping_microservices

2. **Estructura del Proyecto**:

- **docker-comprose.yml** Archivo para orquestar los microservicios.
- **services/scraping** Contiene el código y Dockerfile del servicio de scraping.
- **database/init.sql** Script para inicailziar las tablas en la base de datos PostgresSQL.

3. **Configura el archivo configuraciones en scraping_service.py**

Ajusta los selectores CSS en el archivo `scraping_service.py` según la estructura HTML actual de cada página web. Ejemplo:

```python
configuraciones = {
    "afp_habitat": {
        "url": "https://www.afphabitat.cl/nuestra-empresa/estatutos-y-estados-financieros/",
        "elemento_principal": "div.select",
        "elemento_filas": "div.financial-statements",
        "nombre": "h3",
        "periodo": "span.periodo",
        "fecha": "span.fecha",
    },
    "zofri": {
        "url": "https://www.zofri.cl/es-cl/Financiera/Paginas/EstadosFinancieros.aspx#/collapse1",
        "elemento_principal": "table",
        "elemento_filas": "table tr",
        "nombre": "td:nth-child(1)",
        "periodo": "td:nth-child(1)",
        "fecha": "td:nth-child(2)",
    }
}
```

 ## Instrucciones para Levantar el Proyecto

 1. **Crear el Dockerfile**

 Asegúrate de tener un Dockerfile en `services/scraping` que instale las dependencias necesarias para Selenium y FastAPI. El Dockerfile debería verse así:

 ~~~
    # Utilizar una imagen de Python
FROM python:3.9-slim

# Instalar dependencias necesarias para Selenium y Chrome
RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requirements y instalarlos
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Configuración para Selenium
ENV DISPLAY=:99

# Comando para ejecutar la aplicación
CMD ["uvicorn", "scraping_service:app", "--host", "0.0.0.0", "--port", "8001"]
~~~

2. **Configurar Docker Compose**

 El archivo `docker-compose.yml` debe orquestar los servicios y configurarlos para utilizar la base de datos PostgreSQL.

~~~
services:
  scraping_service:
    build:
      context: ./services/scraping
    ports:
      - "8001:8001"
    volumes:
      - ./services/scraping:/app
    environment:
      - PYTHONUNBUFFERED=1
    command: uvicorn scraping_service:app --host 0.0.0.0 --port 8001
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: scraping_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
~~~

3. **Levanta el Proyecto**

Ejecuta el siguiente comando para construir las imágenes y levantar todos los servicios:

```bash
    docker-compose up --build
```

4. **Verifica los Servicios**

Para verificar que el servicio de scraping está corriendo, abre tu navegador o Postman y realiza una solicitud GET a:

```http
    http://localhost:8001/scrape/afp_habitat
```

## Uso del Servicio de Scraping

El servicio de scraping acepta peticiones GET para diferentes empresas. Por ejemplo:

- Endpoint para AFP Habitat:

```http
GET http://localhost:8001/scrape/afp_habitat
```

Endpoint para Zofri:
```http
GET http://localhost:8001/scrape/zofri
```

Estos endpoints realizarán el scraping y devolverán los datos en formato JSON.

**Ejemplo de Respuesta**

Si el scraping se realiza con éxito, deberías recibir una respuesta en JSON similar a esta:

```json
Copiar código
{
  "empresa": "afp_habitat",
  "data": [
    {
      "nombre": "Estado Financiero Marzo 2023",
      "periodo": "Q1",
      "fecha": "2023-05-30"
    },
    {
      "nombre": "Estado Financiero Junio 2023",
      "periodo": "Q2",
      "fecha": "2023-09-13"
    }
  ]
}

```

**Problemas Comunes**

Error de chromedriver no encontrado: Asegúrate de que chromedriver y chromium están instalados en el contenedor Docker. Puedes verificar la instalación en el Dockerfile.

Puerto 5432 ya en uso: Si ves un error de conflicto de puertos, asegúrate de que no tienes otra instancia de PostgreSQL en el sistema o cambia el puerto externo en docker-compose.yml:

yaml
Copiar código
ports:
  - "5433:5432"
Error 500 Internal Server Error: Verifica los logs de Docker para ver los detalles del error. A menudo, esto se debe a problemas con los selectores CSS en el archivo de configuración del scraping.