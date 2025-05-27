import requests # type: ignore
from typing import Optional, Dict

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

def get_weather_for_sowing(city: str) -> Optional[Dict]:
    weather_data = get_weather(city)
    if weather_data and weather_data.get("main"):
        temp = weather_data["main"]["temp"]
        humidity = weather_data["main"]["humidity"]
        description = weather_data["weather"][0]["description"]
        recommendation = ("Es un buen momento para sembrar, pero asegúrate de regar adecuadamente." 
                         if temp > 20 and humidity < 70 
                         else "Las condiciones no son ideales para sembrar ahora. Considera esperar a que mejore el clima.")
        return {
            "temp": temp,
            "humidity": humidity,
            "description": description,
            "recommendation": recommendation
        }
    return None