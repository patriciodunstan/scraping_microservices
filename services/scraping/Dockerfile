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
