from difflib import get_close_matches
from typing import Dict
import pandas as pd # type: ignore
from .weather_api import get_weather
from .location_handler import extract_location, recommend_crop_by_location
from .nlp_processor import NLPProcessor

class QuestionProcessor:
    def __init__(self, questions_data: Dict, agricultural_data: pd.DataFrame, department_data: pd.DataFrame):
        self.questions_data = questions_data
        self.agricultural_data = agricultural_data
        self.department_data = department_data
        self.nlp_processor = NLPProcessor()
        self.intent_labels = ["theoretical", "weather", "recommendation", "location_based_recommendation", "crop_timing", "irrigation_advice"]

    def process_question(self, user_input: str, city: str = "Bogotá") -> str:
        user_input = user_input.lower().strip()

        # Clasificar la intención usando NLP
        intent = self.nlp_processor.classify_intent(user_input, self.intent_labels)

        # Analizar el sentimiento (opcional, para personalizar respuestas)
        sentiment = self.nlp_processor.analyze_sentiment(user_input)
        sentiment_prefix = "¡Entiendo que estás preocupado! " if sentiment["compound"] < -0.1 else ""

        # Procesar preguntas teóricas
        if intent == "theoretical":
            questions = [q["question"].lower() for q in self.questions_data["theoretical"]]
            matches = get_close_matches(user_input, questions, n=1, cutoff=0.6)
            if matches:
                for q in self.questions_data["theoretical"]:
                    if q["question"].lower() == matches[0]:
                        return sentiment_prefix + q["answer"]

        # Procesar preguntas dinámicas
        dynamic_questions = [q["question"].lower() for q in self.questions_data["dynamic"]]
        matches = get_close_matches(user_input, dynamic_questions, n=1, cutoff=0.6)
        if matches:
            for q in self.questions_data["dynamic"]:
                if q["question"].lower() == matches[0]:
                    if q["type"] == "weather":
                        weather_data = get_weather(city)
                        if weather_data and weather_data.get("main"):
                            temp = weather_data["main"]["temp"]
                            description = weather_data["weather"][0]["description"]
                            return sentiment_prefix + f"El clima en {city} es {description} con una temperatura de {temp}°C."
                        return sentiment_prefix + "No pude obtener los datos climáticos. Por favor, intenta de nuevo."

                    elif q["type"] == "recommendation":
                        return sentiment_prefix + q["answer_template"]

                    elif q["type"] == "location_based_recommendation":
                        department = extract_location(user_input, self.department_data)
                        if department:
                            recommendation = recommend_crop_by_location(department, self.department_data)
                            if recommendation:
                                return sentiment_prefix + q["answer_template"].format(
                                    department=recommendation["department"],
                                    crop=recommendation["crop"]
                                )
                        return sentiment_prefix + "No pude identificar tu departamento. Por favor, indícalo claramente (por ejemplo, 'Antioquia')."

                    elif q["type"] == "crop_timing":
                        crop = None
                        for c in self.agricultural_data["cultivo"].str.lower():
                            if c in user_input:
                                crop = c
                                break
                        if crop:
                            crop_data = self.agricultural_data[self.agricultural_data["cultivo"].str.lower() == crop]
                            if not crop_data.empty:
                                month = crop_data.iloc[0]["mes_siembra"]
                                return sentiment_prefix + q["answer_template"].format(crop=crop, month=month)
                            return sentiment_prefix + f"No tengo información sobre {crop}. ¿Quieres información sobre otro cultivo?"
                        return sentiment_prefix + "Por favor, especifica un cultivo (por ejemplo, 'maíz')."

                    elif q["type"] == "irrigation_advice":
                        weather_data = get_weather(city)
                        recommendation = "hoy no se recomienda el riego." if weather_data and weather_data["main"]["humidity"] > 60 else "puedes considerar regar hoy."
                        return sentiment_prefix + q["answer_template"].format(recommendation=recommendation)

        return sentiment_prefix + "Lo siento, no entiendo tu pregunta. ¿Puedes reformularla o consultar algo específico sobre cultivos o clima?"