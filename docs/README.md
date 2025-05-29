
# Agrobot - Chatbot Agrícola 🌱

![Python](https://img.shields.io/badge/Python-3.11.2-blue)
![Anaconda](https://img.shields.io/badge/Anaconda-24.9.2+-yellow)
![Flask](https://img.shields.io/badge/Flask-2.0.0+-green)
![License](https://img.shields.io/badge/License-MIT-brightgreen)

**Agrobot** es un chatbot basado en inteligencia artificial diseñado para apoyar a pequeños agricultores en la toma de decisiones agrícolas. Ofrece recomendaciones personalizadas sobre siembra, manejo de plagas, uso de químicos y planificación de cultivos según las condiciones climáticas. 🚜

Este proyecto está desarrollado con Python, Flask y herramientas de procesamiento de lenguaje natural, y es ideal para quienes buscan optimizar sus prácticas agrícolas de manera sencilla y accesible.

## Tabla de Contenidos

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
  - [Paso 1: Instalar Anaconda](#paso-1-instalar-anaconda)
  - [Paso 2: Crear un entorno virtual](#paso-2-crear-un-entorno-virtual)
  - [Paso 3: Instalar dependencias](#paso-3-instalar-dependencias)
  - [Paso 4: Entrenar el modelo](#paso-4-entrenar-el-modelo)
  - [Paso 5: Ejecutar la aplicación](#paso-5-ejecutar-la-aplicación)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Uso](#uso)
- [Contribuir](#contribuir)

## Características

- **Recomendaciones personalizadas**: Consejos adaptados sobre siembra, manejo de plagas y planificación de cultivos basados en datos climáticos.
- **Interfaz amigable**: Aplicación web desarrollada con Flask, accesible desde cualquier navegador.
- **Procesamiento de lenguaje natural**: Entiende consultas de los agricultores y responde de manera precisa.
- **Fácil de configurar**: Entorno reproducible con Anaconda y dependencias claras.

## Requisitos

- Sistema operativo: Windows (64 bits recomendado), macOS o Linux.
- Anaconda (versión 24.9.2 o superior).
- Python 3.11.2
- Conexión a internet (para descargar dependencias y Anaconda).
- Navegador web moderno (para acceder a la aplicación).

## Instalación

Sigue estos pasos para configurar **Agrobot** en tu máquina local.

### Paso 1: Instalar Anaconda

1. **Descarga Anaconda**:
   - Visita [https://www.anaconda.com/download](https://www.anaconda.com/download).
   - Selecciona la versión **Individual Edition** para tu sistema operativo (recomendado: 64 bits para Windows).
   - Descarga el instalador (por ejemplo, `Anaconda3-2023.XX-Windows-x86_64.exe`).

2. **Ejecuta el instalador**:
   - Haz doble clic en el archivo descargado.
   - Acepta los términos de la licencia.
   - Selecciona **"Just Me"** (instalación personal) o **"All Users"** (si tienes permisos de administrador).
   - Elige una carpeta de instalación (por defecto: `C:\Users\<TuUsuario>\Anaconda3`).
   - **Recomendado**: Marca la casilla para agregar Anaconda al PATH del sistema.
   - Haz clic en **Install** y espera a que finalice.

3. **Verifica la instalación**:
   - Abre **Anaconda Prompt** desde el menú de inicio.
   - Ejecuta:
     ```bash
     conda --version
     ```
   - Deberías ver una salida como `conda 23.7.4` (la versión puede variar).

### Paso 2: Crear un entorno virtual

1. **Abre Anaconda Prompt**:
   - Busca "Anaconda Prompt" en el menú de inicio.

2. **Crea un entorno virtual**:
   - Crea un entorno llamado `agrobot` con Python 3.11.2:
     ```bash
     conda create -n agrobot python=3.11.2
     ```
   - Confirma con `y` si se solicita instalar paquetes.

3. **Activa el entorno**:
   - Activa el entorno con:
     ```bash
     conda activate agrobot
     ```
   - Verás `(agrobot)` al inicio de la línea de comandos.

4. **Verifica la versión de Python**:
   - Ejecuta:
     ```bash
     python --version
     ```
   - Deberías ver `Python 3.11.2`.

5. **Desactivar o eliminar el entorno** (opcional):
   - Para desactivar el entorno:
     ```bash
     conda deactivate
     ```
   - Para eliminar el entorno:
     ```bash
     conda env remove -n agrobot
     ```

### Paso 3: Instalar dependencias

1. Asegúrate de que el entorno `agrobot` esté activado:
   ```bash
   conda activate agrobot
   ```

2. Instala las dependencias del proyecto:
   - Navega al directorio del proyecto y ejecuta:
     ```bash
     pip install -r requirements.txt
     ```

### Paso 4: Entrenar el modelo

1. Entrena el modelo de procesamiento de lenguaje natural:
   - Ejecuta:
     ```bash
     python train_intent_classifier.py
     ```
   - Nota: Este proceso puede ser intensivo y tardar varios minutos, dependiendo de tu máquina.

2. Limpieza posterior:
   - Una vez completado el entrenamiento, elimina la carpeta `results` generada, ya que contiene checkpoints de entrenamiento que ya no son necesarios:
     ```bash
     rm -rf results
     ```

### Paso 5: Ejecutar la aplicación

1. Inicia la aplicación Flask:
   - Ejecuta:
     ```bash
     python app.py
     ```

2. Accede a la aplicación:
   - Abre un navegador y visita [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Estructura del Proyecto

```plaintext
agrobot/
├── app/                  # Código de la aplicación Flask
├── data/                 # Datasets agrícolas
├── docs/                 # Documentación del proyecto
├── requirements.txt      # Dependencias del proyecto
└── .gitignore            # Archivos ignorados por Git
```

## Uso

1. Asegúrate de que el entorno `agrobot` está activado.
2. Ejecuta `python app.py`.
3. Abre tu navegador en [http://127.0.0.1:5000](http://127.0.0.1:5000).
4. Interactúa con el chatbot ingresando consultas agrícolas (por ejemplo, "¿Cuándo debo sembrar maíz?" o "¿Cómo controlo las plagas en tomates?").
5. Recibe recomendaciones personalizadas basadas en datos climáticos y agrícolas.

## Contribuir

¡Agradecemos las contribuciones! Si deseas colaborar, sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -m "Añadir nueva funcionalidad"`).
4. Sube los cambios a tu fork (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request en este repositorio.

