FROM python:3.11.2-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos del proyecto
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar gunicorn para producción
RUN pip install gunicorn

# Exponer puerto 5000
EXPOSE 5000

# Establecer variables de entorno para Flask
ENV FLASK_ENV=production

# Ejecutar la aplicación con gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]