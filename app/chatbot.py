import json
import pandas as pd
import requests # type: ignore
from difflib import get_close_matches
from typing import Dict, Optional

#configuracion de la API de OpenweatherMap
API_KEY = "e26d3bf8f35fadf47c8481cef283bfcd"
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

#carga de preguntas predefinidas desde un archivo JSON

def load_predefied_questions(file_path: str) -> Dict:
    try:
        with open(file_path, 'r', encoding = 'utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: El archivo {file_path} no se encontró.")
        return {"questions": []}
    
    
#cargar los datos agricolas desde un csv
def load_agricultural_data(file_path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: El archivo {file_path} no se encontró.")
        return pd.DataFrame()

#obtener datos metereologicos en tiempo real
def get_weather(city: str) -> Optional[Dict]:
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "es"
    }
    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()  # Lanza un error si la respuesta no es exitosa
        return response.json()
    except requests.RequestException as e:
        print(f"Error al consultar la API del clima: {e}")
        return None
