import requests # type: ignore
from typing import Optional, Dict
#Este archivo manejará las consultas a la API de OpenWeatherMap.
API_KEY = "e26d3bf8f35fadf47c8481cef283bfcd"
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

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