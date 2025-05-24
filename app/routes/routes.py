from flask import Blueprint, render_template, request # type: ignore
from ..chatbot import init_chatbot

bp = Blueprint('main', __name__)

# Inicializar el procesador de preguntas
processor = init_chatbot()

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/chat', methods=['GET', 'POST'])
def chat():
    response = None
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        response = processor.process_question(user_input)
    return render_template('chat.html', response=response)

@bp.route('/weather')
def weather():
    weather_data = {
        "temperature": 22,
        "humidity": 65,
        "recommendation": "Hoy no se recomienda el riego."
    }
    return render_template('weather.html', weather_data=weather_data)

@bp.route('/recommendations')
def recommendations():
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
        "irrigation_need": 90,
        "pests_detected": 10,
        "message": "El crecimiento de los cultivos es bueno. Se requiere riego pronto. Una plaga ha sido detectada. Recomiendo tomar acción."
    }
    return render_template('crop_status.html', crop_data=crop_data)

@bp.route('/support')
def support():
    return render_template('support.html')