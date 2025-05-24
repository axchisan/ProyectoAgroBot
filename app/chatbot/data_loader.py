import json
import pandas as pd # type: ignore
from typing import Dict
#Este archivo manejará la carga de datos (JSON y CSV).

def load_questions(file_path: str) -> Dict:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
        return {"theoretical": [], "dynamic": []}

def load_agricultural_data(file_path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
        return pd.DataFrame()

def load_department_data(file_path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
        return pd.DataFrame()
    
