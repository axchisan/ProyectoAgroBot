from difflib import get_close_matches
from typing import Dict
import pandas as pd
import requests
import re
from .weather_api import get_weather, get_weather_for_sowing
from .location_handler import (extract_location, recommend_crop_by_location, 
                              get_production_data, get_crop_profitability, 
                              get_department_with_min_production, get_department_with_max_production)
from .nlp_processor import NLPProcessor

class QuestionProcessor:
    def __init__(self, questions_data: Dict, agricultural_data: pd.DataFrame, department_data: pd.DataFrame, api_key: str = None):
        self.questions_data = questions_data
        self.agricultural_data = agricultural_data
        self.department_data = department_data
        self.nlp_processor = NLPProcessor()
        self.api_key = api_key  # API key para el modelo externo (como xAI)
        self.intent_labels = [
            "theoretical", "weather", "weather_forecast", "weather_sowing_advice", "current_location",
            "recommendation", "location_based_recommendation", "crop_profitability", 
            "crop_production", "crop_timing", "irrigation_advice"
        ]

    def normalize_text(self, text: str) -> str:
        """Normaliza el texto para mejorar coincidencias."""
        text = text.lower().strip()
        text = re.sub(r'[¿¡!?,.;]', '', text)
        return text

    def extract_crop(self, user_input: str) -> str:
        """Extrae el cultivo mencionado en la entrada del usuario."""
        crops = ["maíz", "papa", "café", "tomate", "arroz", "guayaba", "plátano", "cacao", "yuca", "caña de azúcar"]
        user_input = user_input.lower()
        for crop in crops:
            if crop in user_input:
                return crop
        return None

    def call_external_api(self, user_input: str) -> str:
        """Llama a una API externa (como xAI) para responder preguntas no manejadas."""
        if not self.api_key:
            return "No tengo acceso a una API externa para responder esta pregunta."
        
        try:
            # Simulación de una llamada a la API (reemplaza con tu implementación real)
            url = "https://api.x.ai/grok/v1/answer"  # Ejemplo de endpoint
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {"question": user_input}
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json().get("answer", "No obtuve respuesta de la API.")
        except Exception as e:
            return f"Error al consultar la API externa: {str(e)}"

    def process_question(self, user_input: str, city: str = "Bogotá", department: str = "Cundinamarca") -> str:
        user_input_normalized = self.normalize_text(user_input)
        user_input = user_input.lower().strip()

        # Clasificar la intención usando NLP
        intent = self.nlp_processor.classify_intent(user_input, self.intent_labels)
        print(f"Intención clasificada para '{user_input}': {intent}")

        # Analizar el sentimiento
        sentiment = self.nlp_processor.analyze_sentiment(user_input)
        sentiment_prefix = "¡Entiendo que estás preocupado! " if sentiment["compound"] < -0.1 else ""

        # Procesar preguntas teóricas
        if intent == "theoretical":
            questions = [self.normalize_text(q["question"]) for q in self.questions_data["theoretical"]]
            matches = get_close_matches(user_input_normalized, questions, n=1, cutoff=0.4)
            if matches:
                for q in self.questions_data["theoretical"]:
                    if self.normalize_text(q["question"]) == matches[0]:
                        return sentiment_prefix + q["answer"]

        # Procesar preguntas dinámicas
        dynamic_questions = [self.normalize_text(q["question"]) for q in self.questions_data["dynamic"]]
        matches = get_close_matches(user_input_normalized, dynamic_questions, n=1, cutoff=0.4)
        if matches:
            for q in self.questions_data["dynamic"]:
                if self.normalize_text(q["question"]) == matches[0]:
                    # Clima
                    if q["type"] in ["weather", "weather_sowing_advice"]:
                        target_city = city
                        location = extract_location(user_input, self.department_data)
                        if location and location.get("city"):
                            target_city = location["city"]
                        if q["type"] == "weather":
                            weather_data = get_weather(target_city)
                            if weather_data and "main" in weather_data:
                                temp = weather_data["main"]["temp"]
                                description = weather_data["weather"][0]["description"]
                                return sentiment_prefix + q["answer_template"].format(city=target_city, description=description, temp=temp)
                            return sentiment_prefix + "No pude obtener los datos climáticos. Por favor, intenta de nuevo."
                        elif q["type"] == "weather_sowing_advice":
                            weather_data = get_weather_for_sowing(target_city)
                            if weather_data:
                                return sentiment_prefix + q["answer_template"].format(
                                    city=target_city,
                                    description=weather_data["description"],
                                    temp=weather_data["temp"],
                                    humidity=weather_data["humidity"],
                                    recommendation=weather_data["recommendation"]
                                )
                            return sentiment_prefix + "No pude obtener los datos climáticos para evaluar la siembra."

                    # Pronósticos futuros
                    elif q["type"] == "weather_forecast":
                        return sentiment_prefix + q["answer_template"]

                    # Ubicación actual
                    elif q["type"] == "current_location":
                        return sentiment_prefix + q["answer_template"].format(city=city, department=department)

                    # Recomendaciones generales
                    elif q["type"] == "recommendation":
                        location = extract_location(user_input, self.department_data)
                        if location and location.get("department"):
                            recommendation = recommend_crop_by_location(location["department"], self.department_data)
                            if recommendation:
                                return sentiment_prefix + f"Basado en tu ubicación en {location['department']}, te recomiendo sembrar {recommendation['crop']} con un rendimiento esperado de {recommendation['yield']} toneladas por hectárea."
                        return sentiment_prefix + q["answer_template"]

                    # Recomendaciones basadas en ubicación
                    elif q["type"] == "location_based_recommendation":
                        target_dept = department
                        location = extract_location(user_input, self.department_data)
                        if location and location.get("department"):
                            target_dept = location["department"]
                        recommendation = recommend_crop_by_location(target_dept, self.department_data)
                        if recommendation and "crop" in recommendation and "yield" in recommendation:
                            return sentiment_prefix + q["answer_template"].format(
                                department=recommendation["department"],
                                crop=recommendation["crop"],
                                yield_value=recommendation["yield"]
                            )
                        return sentiment_prefix + "No pude identificar tu departamento o no tengo datos para recomendar cultivos."

                    # Rentabilidad de cultivos
                    elif q["type"] == "crop_profitability":
                        crop = self.extract_crop(user_input)
                        target_dept = extract_location(user_input, self.department_data)
                        if target_dept and target_dept.get("department"):
                            recommendation = recommend_crop_by_location(target_dept["department"], self.department_data)
                            if recommendation and "crop" in recommendation and "yield" in recommendation:
                                return sentiment_prefix + q["answer_template"].format(
                                    department=recommendation["department"],
                                    crop=recommendation["crop"],
                                    yield_value=recommendation["yield"]
                                )
                        elif crop:
                            profitability = get_crop_profitability(crop, self.department_data)
                            if profitability and "crop" in profitability and "yield" in profitability:
                                return sentiment_prefix + q["answer_template"].format(
                                    crop=profitability["crop"],
                                    department=profitability["department"],
                                    yield_value=profitability["yield"]
                                )
                        return sentiment_prefix + "No pude identificar el cultivo o no tengo datos de rentabilidad."

                    # Producción de cultivos
                    elif q["type"] == "crop_production":
                        crop = self.extract_crop(user_input)
                        target_dept = extract_location(user_input, self.department_data)
                        if target_dept and target_dept.get("department"):
                            production = get_production_data(crop, target_dept["department"], self.department_data)
                            if production and "production" in production:
                                return sentiment_prefix + q["answer_template"].format(
                                    crop=production["crop"],
                                    department=production["department"],
                                    production=production["production"]
                                )
                        elif "menos" in user_input:
                            min_production = get_department_with_min_production(crop, self.department_data)
                            if min_production and "production" in min_production:
                                return sentiment_prefix + q["answer_template"].format(
                                    crop=min_production["crop"],
                                    department=min_production["department"],
                                    production=min_production["production"]
                                )
                        elif "más" in user_input:
                            max_production = get_department_with_max_production(crop, self.department_data)
                            if max_production and "production" in max_production:
                                return sentiment_prefix + q["answer_template"].format(
                                    crop=max_production["crop"],
                                    department=max_production["department"],
                                    production=max_production["production"]
                                )
                        return sentiment_prefix + "No pude identificar el cultivo o no tengo datos de producción."

                    # Tiempo de siembra
                    elif q["type"] == "crop_timing":
                        crop = self.extract_crop(user_input)
                        if crop:
                            crop_data = self.agricultural_data[self.agricultural_data["cultivo"].str.lower() == crop]
                            if not crop_data.empty:
                                month = crop_data.iloc[0]["mes_siembra"]
                                return sentiment_prefix + q["answer_template"].format(crop=crop, month=month)
                            return sentiment_prefix + f"No tengo información sobre {crop}. ¿Quieres información sobre otro cultivo?"
                        return sentiment_prefix + "Por favor, especifica un cultivo (por ejemplo, 'maíz')."

                    # Consejos de riego
                    elif q["type"] == "irrigation_advice":
                        target_city = city
                        location = extract_location(user_input, self.department_data)
                        if location and location.get("city"):
                            target_city = location["city"]
                        weather_data = get_weather(target_city)
                        if weather_data and "main" in weather_data:
                            recommendation = ("hoy no se recomienda el riego." 
                                             if weather_data["main"]["humidity"] > 60 
                                             else "puedes considerar regar hoy.")
                            return sentiment_prefix + q["answer_template"].format(city=target_city, recommendation=recommendation)
                        return sentiment_prefix + "No pude obtener los datos climáticos para dar un consejo de riego."

        # Si no se encuentra una respuesta, intentar con la API externa
        return sentiment_prefix + self.call_external_api(user_input)