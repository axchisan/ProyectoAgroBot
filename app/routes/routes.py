from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from ..chatbot import init_chatbot
import os
from ..chatbot.weather_api import get_weather, get_forecast, get_weather_for_sowing
from ..chatbot.location_handler import get_location_from_coords
from datetime import datetime

bp = Blueprint('main', __name__)

# Inicializar el chatbot con la clave API de OpenWeatherMap desde el entorno
processor = init_chatbot(weather_api_key=os.getenv("OPENWEATHERMAP_API_KEY"))

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'chat_history' not in session:
        session['chat_history'] = [
            {"role": "agrobot", "message": "Hola, soy AGROBOT 🌱. ¿Cómo puedo ayudarte hoy?", "timestamp": datetime.now().strftime('%H:%M')}
        ]

    if request.method == 'POST':
        user_input = request.form.get('user_input')
        lat = session.get('lat')
        lon = session.get('lon')
        city = session.get('city', 'Guavatá')
        department = session.get('department', 'Santander')
        
        response = processor.process_question(user_input, city=city, department=department, lat=lat, lon=lon)
        
        # Agregar mensajes con timestamp
        session['chat_history'].append({"role": "user", "message": user_input, "timestamp": datetime.now().strftime('%H:%M')})
        session['chat_history'].append({"role": "agrobot", "message": response, "timestamp": datetime.now().strftime('%H:%M')})
        
        session.modified = True

        if "estoy en" in user_input.lower() or "mi ciudad es" in user_input.lower():
            new_location = processor.extract_location(user_input)
            if new_location:
                session['city'] = new_location.get('city', city)
                session['department'] = new_location.get('department', department)

    return render_template('chat.html', chat_history=session['chat_history'])

@bp.route('/clear_chat', methods=['GET'])
def clear_chat():
    session['chat_history'] = [
        {"role": "agrobot", "message": "Hola, soy AGROBOT 🌱. ¿Cómo puedo ayudarte hoy?", "timestamp": datetime.now().strftime('%H:%M')}
    ]
    session.modified = True
    return redirect(url_for('main.chat'))


@bp.route('/weather')
def weather():
    city = session.get('city', 'Guavatá')
    department = session.get('department', 'Santander')
    
    weather_data = get_weather(city, api_key=os.getenv("OPENWEATHERMAP_API_KEY"))
    sowing_data = get_weather_for_sowing(city, api_key=os.getenv("OPENWEATHERMAP_API_KEY"))
    
    forecast_data = get_forecast(city, api_key=os.getenv("OPENWEATHERMAP_API_KEY"))
    
    if weather_data and weather_data.get('main') and sowing_data:
        weather_info = {
            "city": city,
            "department": department,
            "temperature": round(weather_data["main"]["temp"]),
            "feels_like": round(weather_data["main"]["feels_like"]),
            "humidity": weather_data["main"]["humidity"],
            "description": weather_data["weather"][0]["description"].capitalize(),
            "wind_speed": round(weather_data["wind"]["speed"] * 3.6, 1),
            "visibility": weather_data.get("visibility", 10000) / 1000,
            "pressure": weather_data["main"]["pressure"],
            "icon_code": weather_data["weather"][0]["icon"],
            "sowing_recommendation": sowing_data["recommendation"],
            "irrigation_recommendation": (
                "Evita regar en exceso, ya que la humedad es alta."
                if weather_data["main"]["humidity"] > 70
                else "Riega tus cultivos, ya que la humedad es baja."
            )
        }
        
        forecast_list = []
        if forecast_data:
            days = ["Hoy", "Mañana", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            for i, forecast in enumerate(forecast_data):
                forecast_list.append({
                    "day": days[i % 7],
                    "temp_max": round(forecast["temp_max"]),
                    "temp_min": round(forecast["temp_min"]),
                    "description": forecast["description"].capitalize(),
                    "icon_code": forecast["icon"]
                })
            while len(forecast_list) < 7:
                last_forecast = forecast_list[-1].copy()
                last_forecast["day"] = days[len(forecast_list) % 7]
                forecast_list.append(last_forecast)
        
        return render_template('weather.html', weather_data=weather_info, forecast_data=forecast_list)
    return render_template('weather.html', weather_data={"error": "No se pudo obtener el clima para " + city})

@bp.route('/refresh_weather', methods=['GET'])
def refresh_weather():
    city = session.get('city', 'Guavatá')
    department = session.get('department', 'Santander')
    
    weather_data = get_weather(city, api_key=os.getenv("OPENWEATHERMAP_API_KEY"))
    sowing_data = get_weather_for_sowing(city, api_key=os.getenv("OPENWEATHERMAP_API_KEY"))
    
    forecast_data = get_forecast(city, api_key=os.getenv("OPENWEATHERMAP_API_KEY"))
    
    if weather_data and weather_data.get('main') and sowing_data:
        weather_info = {
            "city": city,
            "department": department,
            "temperature": round(weather_data["main"]["temp"]),
            "feels_like": round(weather_data["main"]["feels_like"]),
            "humidity": weather_data["main"]["humidity"],
            "description": weather_data["weather"][0]["description"].capitalize(),
            "wind_speed": round(weather_data["wind"]["speed"] * 3.6, 1),
            "visibility": weather_data.get("visibility", 10000) / 1000,
            "pressure": weather_data["main"]["pressure"],
            "icon_code": weather_data["weather"][0]["icon"],
            "sowing_recommendation": sowing_data["recommendation"],
            "irrigation_recommendation": (
                "Evita regar en exceso, ya que la humedad es alta."
                if weather_data["main"]["humidity"] > 70
                else "Riega tus cultivos, ya que la humedad es baja."
            )
        }
        
        forecast_list = []
        if forecast_data:
            days = ["Hoy", "Mañana", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            for i, forecast in enumerate(forecast_data):
                forecast_list.append({
                    "day": days[i % 7],
                    "temp_max": round(forecast["temp_max"]),
                    "temp_min": round(forecast["temp_min"]),
                    "description": forecast["description"].capitalize(),
                    "icon_code": forecast["icon"]
                })
            while len(forecast_list) < 7:
                last_forecast = forecast_list[-1].copy()
                last_forecast["day"] = days[len(forecast_list) % 7]
                forecast_list.append(last_forecast)
        
        return jsonify({"success": True, "weather": weather_info, "forecast": forecast_list})
    return jsonify({"success": False, "error": "No se pudo obtener el clima para " + city})

@bp.route('/update_location', methods=['POST'])
def update_location():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    if lat is not None and lon is not None:
        session['lat'] = float(lat)
        session['lon'] = float(lon)
        location = get_location_from_coords(lat, lon)
        if location:
            session['city'] = location.get('city', 'Guavatá')
            session['department'] = location.get('department', 'Santander')
        session.modified = True
        return jsonify({"success": True})
    return jsonify({"error": "No se proporcionaron coordenadas válidas."}), 400

@bp.route('/recommendations')
def recommend():
    recommendations_data = [
        {"icon": "corn", "text": "Mejor fecha de siembra"},
        {"icon": "wheat", "text": "Tipo de fertilizante"},
        {"icon": "sunflower", "text": "Rotación de cultivos"}
    ]
    return render_template('recommendations.html', recommendations=recommendations_data)

@bp.route('/crop_status')
def crop_status():
    crop_data = {
        "growth_level": 70,
        "irrigation_needed": 90,
        "pests_detected": 10,
        "message": "El crecimiento de los cultivos es bueno. Se requiere riego pronto. Una plaga ha sido detectada. Recomiendo tomar acción."
    }
    return render_template('crop_status.html', crop_data=crop_data)

@bp.route('/support')
def support():
    return render_template('support.html')