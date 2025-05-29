import json
import pandas as pd # type: ignore
import os
from typing import Dict


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
    # Carga un CSV con datos agrícolas, como cultivos, meses de siembra y rendimientos.
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

def load_dynamic_datasets(data_dir: str = "data/processed") -> Dict[str, pd.DataFrame]:
    # Carga dinámicamente todos los CSV en las subcarpetas de data_dir.
    # Retorna un diccionario con el nombre del archivo sin .csv como clave y el DataFrame como valor.
    datasets = {}
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                key = file.replace(".csv", "").lower()
                try:
                    df = pd.read_csv(file_path)
                    datasets[key] = df
                except Exception as e:
                    print(f"Error al cargar {file_path}: {e}")
    return datasets