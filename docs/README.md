Agrobot - Chatbot Agrícola
Descripción:
Agrobot es un chatbot basado en inteligencia artificial diseñado para asistir a pequeños agricultores en la toma de decisiones agrícolas. Proporciona recomendaciones personalizadas sobre siembra, manejo de plagas, uso de químicos, y planificación de cultivos según el clima.
Instalación

Instalar Anaconda:

Sigue las instrucciones para tu sistema operativo.


Crear entorno virtual:
conda create -n agrobot python=3.11
conda activate agrobot
tambien puedes crear un entorno virtual con venv en python

Instalar dependencias:
pip install -r requirements.txt


Ejecutar la aplicación:
python app.py

Abre http://127.0.0.1:5000 en tu navegador.


Estructura del Proyecto

app/: Código de la aplicación Flask.
data/: Datasets agrícolas.
docs/: Documentación del proyecto.
requirements.txt: Dependencias.
.gitignore: Archivos ignorados por Git.

