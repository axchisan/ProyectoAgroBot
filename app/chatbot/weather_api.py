import requests
from typing import Optional, Dict, List
import os
from datetime import datetime, timedelta

WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_API_URL = "http://api.openweathermap.org/data/2.5/forecast"

def get_weather(city: str, api_key: str = None) -> Optional[Dict]:
    """
    Obtiene el clima actual para una ciudad dada usando OpenWeatherMap.
    
    Args:
        city (str): Nombre de la ciudad.
        api_key (str, optional): Clave API de OpenWeatherMap.
        
    Returns:
        Dict con datos del clima o None si falla.
    """
    api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("Error: No se proporcionó una clave API para OpenWeatherMap.")
        return None
        
    params = {
        "q": city,
        "appid": api_key,
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

def get_weather_by_coords(lat: float, lon: float, api_key: str = None) -> Optional[Dict]:
    """
    Obtiene el clima actual usando coordenadas geográficas.
    
    Args:
        lat (float): Latitud.
        lon (float): Longitud.
        api_key (str, optional): Clave API de OpenWeatherMap.
        
    Returns:
        Dict con datos del clima o None si falla.
    """
    api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("Error: No se proporcionó una clave API para OpenWeatherMap.")
        return None
        
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
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

def get_forecast(city: str, api_key: str = None) -> Optional[List[Dict]]:
    """
    Obtiene el pronóstico de 5 días para una ciudad dada usando OpenWeatherMap.
    
    Args:
        city (str): Nombre de la ciudad.
        api_key (str, optional): Clave API de OpenWeatherMap.
        
    Returns:
        Lista de dicts con el pronóstico diario o None si falla.
    """
    api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("Error: No se proporcionó una clave API para OpenWeatherMap.")
        return None
        
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "es"
    }
    try:
        response = requests.get(FORECAST_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Agrupar datos por día (OpenWeatherMap devuelve datos cada 3 horas)
        daily_forecast = {}
        for entry in data["list"]:
            date = datetime.fromtimestamp(entry["dt"]).date()
            if date not in daily_forecast:
                daily_forecast[date] = {
                    "temp_max": entry["main"]["temp"],
                    "temp_min": entry["main"]["temp"],
                    "description": entry["weather"][0]["description"],
                    "icon": entry["weather"][0]["icon"]
                }
            else:
                daily_forecast[date]["temp_max"] = max(daily_forecast[date]["temp_max"], entry["main"]["temp"])
                daily_forecast[date]["temp_min"] = min(daily_forecast[date]["temp_min"], entry["main"]["temp"])
        
        # Convertir a lista y tomar los primeros 5 días
        forecast_list = []
        today = datetime.now().date()
        for i in range(5):
            forecast_date = today + timedelta(days=i)
            if forecast_date in daily_forecast:
                forecast = daily_forecast[forecast_date]
                forecast["date"] = forecast_date
                forecast_list.append(forecast)
            else:
                # Si no hay datos para un día futuro, repetir el último día
                if forecast_list:
                    last_forecast = forecast_list[-1].copy()
                    last_forecast["date"] = forecast_date
                    forecast_list.append(last_forecast)
        
        return forecast_list
    except requests.RequestException as e:
        print(f"Error al consultar el pronóstico: {e}")
        return None

def get_weather_for_sowing(city: str, api_key: str = None) -> Optional[Dict]:
    """
    Obtiene el clima y una recomendación para siembra en una ciudad dada.
    
    Args:
        city (str): Nombre de la ciudad.
        api_key (str, optional): Clave API de OpenWeatherMap.
        
    Returns:
        Dict con datos del clima y recomendación o None si falla.
    """
    weather_data = get_weather(city, api_key)
    if weather_data and weather_data.get("main"):
        temp = weather_data["main"]["temp"]
        humidity = weather_data["main"]["humidity"]
        description = weather_data["weather"][0]["description"]
        recommendation = (
            "Es un buen momento para sembrar, pero asegúrate de regar adecuadamente."
            if temp > 20 and humidity < 70
            else "Las condiciones no son ideales para sembrar ahora. Considera esperar a que mejore el clima."
        )
        return {
            "city": city,
            "temp": temp,
            "humidity": humidity,
            "description": description,
            "recommendation": recommendation
        }
    return None

def get_weather_for_sowing_by_coords(lat: float, lon: float, api_key: str = None) -> Optional[Dict]:
    """
    Obtiene el clima y una recomendación para siembra usando coordenadas.
    
    Args:
        lat (float): Latitud.
        lon (float): Longitud.
        api_key (str, optional): Clave API de OpenWeatherMap.
        
    Returns:
        Dict con datos del clima y recomendación o None si falla.
    """
    weather_data = get_weather_by_coords(lat, lon, api_key)
    if weather_data and weather_data.get("main"):
        temp = weather_data["main"]["temp"]
        humidity = weather_data["main"]["humidity"]
        description = weather_data["weather"][0]["description"]
        recommendation = (
            "Es un buen momento para sembrar, pero asegúrate de regar adecuadamente."
            if temp > 20 and humidity < 70
            else "Las condiciones no son ideales para sembrar ahora. Considera esperar a que mejore el clima."
        )
        return {
            "city": weather_data.get("name", "Ubicación desconocida"),
            "temp": temp,
            "humidity": humidity,
            "description": description,
            "recommendation": recommendation
        }
    return None