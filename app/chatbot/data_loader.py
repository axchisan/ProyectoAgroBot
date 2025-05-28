import json
import pandas as pd # type: ignore
from typing import Dict
# Este archivo se encarga de cargar datos desde archivos externos para usarlos en Agrobot.
# json maneja archivos JSON,  para estructurar preguntas y respuestas.
# pandas es la librería  para manipular datos tabulares (CSV), optimizando el análisis de datos agrícolas.

def load_questions(file_path: str) -> Dict:
    # Carga un archivo JSON que contiene preguntas predefinidas (teóricas y dinámicas) con sus respuestas o plantillas.
    # Retorna un diccionario; si el archivo no existe, devuelve un diccionario vacío con claves por defecto.
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
        return {"theoretical": [], "dynamic": []}

def load_agricultural_data(file_path: str) -> pd.DataFrame:
    # Carga un de CSV con datos agrícolas, com o cultivos, meses de siembra y rendimientos.
    
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
        return pd.DataFrame()

def load_department_data(file_path: str) -> pd.DataFrame:
    # Carga un CSV con datos de departamentos colombianos, incluyendo producción y cultivos destacados.
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
        return pd.DataFrame()