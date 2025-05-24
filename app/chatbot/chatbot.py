import json
import pandas as pd # type: ignore
import requests # type: ignore
from difflib import get_close_matches
from typing import Dict, Optional

# C API de OpenWeatherMap
API_KEY = "e26d3bf8f35fadf47c8481cef283bfcd"  # Reemplaza con tu clave de OpenWeatherMap
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

# Cargar preguntas predefinidas desde un archivo JSON
def load_predefined_questions(file_path: str) -> Dict:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
        return {"questions": []}

# Cargar datos agrícolas desde un CSV
def load_agricultural_data(file_path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
        return pd.DataFrame()

# Obtener datos meteorológicos en tiempo real
def get_weather(city: str) -> Optional[Dict]:
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "es"
    }
    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error al consultar la API de clima: {e}")
        return None

# Procesar la pregunta del usuario
def process_question(user_input: str, questions_data: Dict, agricultural_data: pd.DataFrame, city: str = "Bogotá") -> str:
    # Normalizar la entrada del usuario
    user_input = user_input.lower().strip()

    # Buscar coincidencias con preguntas predefinidas
    questions = [q["question"].lower() for q in questions_data["questions"]]
    matches = get_close_matches(user_input, questions, n=1, cutoff=0.6)

    if matches:
        # Encontrar la respuesta correspondiente
        for q in questions_data["questions"]:
            if q["question"].lower() == matches[0]:
                return q["answer"]

    # Lógica específica para preguntas relacionadas con el clima
    if any(keyword in user_input for keyword in ["clima", "tiempo", "pronóstico"]):
        weather_data = get_weather(city)
        if weather_data and weather_data.get("main"):
            temp = weather_data["main"]["temp"]
            description = weather_data["weather"][0]["description"]
            return f"El clima en {city} es {description} con una temperatura de {temp}°C."
        return "No pude obtener los datos climáticos. Por favor, intenta de nuevo."

    # Lógica específica para recomendaciones de siembra
    if any(keyword in user_input for keyword in ["sembrar", "siembra", "cultivar"]):
        crop = None
        for c in agricultural_data["cultivo"].str.lower():
            if c in user_input:
                crop = c
                break
        if crop:
            crop_data = agricultural_data[agricultural_data["cultivo"].str.lower() == crop]
            if not crop_data.empty:
                month = crop_data.iloc[0]["mes_siembra"]
                return f"El mejor momento para sembrar {crop} es en {month}."
            return f"No tengo información sobre {crop}. ¿Quieres información sobre otro cultivo?"

    # Respuesta por defecto si no hay coincidencia
    return "Lo siento, no entiendo tu pregunta. ¿Puedes reformularla o consultar algo específico sobre cultivos o clima?" #modelo de respaldo

# Función principal para inicializar el chatbot
def init_chatbot():
    # Cargar datos
    questions_data = load_predefined_questions("data/questions.json")
    agricultural_data = load_agricultural_data("data/processed/crops_data.csv")
    return questions_data, agricultural_data

# Ejemplo de uso
if __name__ == "__main__":
    questions_data, agricultural_data = init_chatbot()
    # Simulación de entrada del usuario
    user_input = "¿Cuándo debo sembrar maíz?"
    response = process_question(user_input, questions_data, agricultural_data)
    print(response)