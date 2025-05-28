from flask import Blueprint, render_template, request, session, redirect, url_for  # type: ignore
from ..chatbot import init_chatbot

bp = Blueprint('main', __name__)


processor = init_chatbot()

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/chat', methods=['GET', 'POST'])
def chat():
    # Inicializar el historial en la sesión si no existe
    if 'chat_history' not in session:
        session['chat_history'] = [
            {"role": "agrobot", "message": "Hola, soy AGROBOT 🌱. ¿Cómo puedo ayudarte hoy?"}
        ]

    if request.method == 'POST':
        user_input = request.form.get('user_input')
        # Obtener la ciudad y el departamento de la sesión, o usar valores por defecto
        city = session.get('city', 'Bogotá')
        department = session.get('department', 'Cundinamarca')
        
        # Procesar la pregunta
        response = processor.process_question(user_input, city, department)
        
        # Añadir la pregunta  y la respuesta de Agrobot al historial
        session['chat_history'].append({"role": "user", "message": user_input})
        session['chat_history'].append({"role": "agrobot", "message": response})
        
        # Guardar los cambios en la sesión
        session.modified = True

        # Si el usuario menciona una ciudad o departamento, actualizar la sesión
        if "estoy en" in user_input.lower() or "mi ciudad es" in user_input.lower():
            new_location = processor.extract_location(user_input)
            if new_location:
                session['city'] = new_location.get('city', city)
                session['department'] = new_location.get('department', department)

    return render_template('chat.html', chat_history=session['chat_history'])

@bp.route('/clear_chat', methods=['GET'])
def clear_chat():
    # Reiniciar el historial de chat con solo el mensaje de bienvenida
    session['chat_history'] = [
        {"role": "agrobot", "message": "Hola, soy AGROBOT 🌱. ¿Cómo puedo ayudarte hoy?"}
    ]
    session.modified = True
    return redirect(url_for('main.chat'))

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