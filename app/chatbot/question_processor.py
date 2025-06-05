from difflib import get_close_matches
from typing import Dict, Optional
import pandas as pd
import requests
import re
from unidecode import unidecode
from .weather_api import get_weather, get_weather_for_sowing
from .location_handler import (extract_location, recommend_crop_by_location, 
                              get_production_data, get_crop_profitability, 
                              get_department_with_min_production, get_department_with_max_production)
from .nlp_processor import NLPProcessor
from .dataset_processor import DatasetProcessor

class QuestionProcessor:
    def __init__(self, questions_data: Dict, agricultural_data: pd.DataFrame, department_data: pd.DataFrame, dataset_processor: DatasetProcessor, api_key: str = None, api_type: str = "openai"):
        self.questions_data = questions_data
        self.agricultural_data = agricultural_data
        self.department_data = department_data
        self.dataset_processor = dataset_processor
        self.nlp_processor = NLPProcessor()
        self.api_key = api_key
        self.api_type = api_type.lower()
        self.intent_labels = [
            "theoretical", "weather", "weather_forecast", "weather_sowing_advice", "current_location",
            "recommendation", "location_based_recommendation", "crop_profitability", 
            "crop_production", "crop_timing", "irrigation_advice",
            "least_favorable_department", "recommended_crops", "production_query"
        ]
        self.context = {
            "department": None,
            "city": None,
            "last_crop": None
        }
        self.initial_prompt = (
            "Eres un complemento para el desarrollo de Agrobot, un chatbot colombiano diseñado para ayudar a pequeños agricultores. "
            "Tu rol es resolver preguntas que Agrobot no puede responder, ofreciendo conceptos, consejos y recomendaciones sobre cultivos, "
            "agricultura sostenible, manejo de plagas, y otros temas agrícolas relevantes para campesinos en Colombia. "
            "Responde siempre en español, de manera clara, práctica y adaptada al contexto colombiano, usando un lenguaje sencillo y limitándote estrictamente a 400 palabras como máximo sin exceder este límite bajo ninguna circunstancia. "
            "Si la pregunta es sobre técnicas agrícolas (como poda, siembra, recolección o manejo de plagas), proporciona pasos específicos, enumera las razones o beneficios, "
            "y asegura que la respuesta sea útil para un agricultor con conocimientos básicos. Cada respuesta debe tener al menos 150 palabras, "
            "evitando errores ortográficos o tipográficos."
        )

    def normalize_text(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r'\bq\b', 'que', text)
        text = re.sub(r'\bk\b', 'que', text)
        text = re.sub(r'\bcultvio\b', 'cultivo', text)
        text = re.sub(r'\bregn\b', 'region', text)
        text = re.sub(r'\bregin\b', 'region', text)
        text = re.sub(r'\bdepto\b', 'departamento', text)
        text = re.sub(r'\bdept\b', 'departamento', text)
        text = unidecode(text)
        text = re.sub(r'[¿¡!?,.;]', '', text)
        return text

    def extract_crop(self, user_input: str) -> Optional[str]:
        crops = [
            "maíz", "maiz", "papa", "café", "cafe", "tomate", "arroz", "guayaba", "plátano", "platano",
            "cacao", "yuca", "caña de azúcar", "caña de azucar", "caña azucarera", "caña panelera",
            "mora", "piña", "aguacate", "mango", "fresa", "guanábana", "limón", "naranja", "mandarina"
        ]
        user_input = self.normalize_text(user_input)
        for crop in crops:
            if self.normalize_text(crop) in user_input:
                self.context["last_crop"] = crop
                return crop
        return self.context.get("last_crop")

    def extract_year(self, user_input: str) -> Optional[int]:
        match = re.search(r'\b(20\d{2})\b', user_input)
        if match:
            return int(match.group(0))
        return None

    def update_context(self, user_input: str):
        location = extract_location(user_input, self.department_data)
        if location:
            if location.get("department"):
                self.context["department"] = location["department"]
            if location.get("city"):
                self.context["city"] = location["city"]

    def call_external_api(self, user_input: str) -> str:
        if not self.api_key and self.api_type == "openai":
            return "No tengo acceso a una API externa. Configura una clave API para respuestas avanzadas."
        full_prompt = f"{self.initial_prompt}\nPregunta del usuario: {user_input}"
        try:
            if self.api_type == "openai":
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "gpt-4o-mini",
                    "store": True,
                    "messages": [
                        {"role": "system", "content": self.initial_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    "max_tokens": 400,
                    "temperature": 0.3
                }
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()
                raw_response = response.json()["choices"][0]["message"]["content"].strip()
                raw_response = re.sub(r'\b(\w+)(\w)\2+\b', r'\1\2', raw_response)
                raw_response = re.sub(r'\s+', ' ', raw_response)
                return raw_response
            else:
                return "Tipo de API no soportado. Usa 'openai'."
        except requests.exceptions.HTTPError as e:
            return f"Error al consultar la API externa: {str(e)}."
        except requests.exceptions.RequestException as e:
            return f"Error de conexión con la API externa: {str(e)}."
        except KeyError as e:
            return f"Error al procesar la respuesta de la API: {str(e)}."

    def process_question(self, user_input: str, city: str = "Bogotá", department: str = "Cundinamarca") -> str:
        user_input_normalized = self.normalize_text(user_input)
        sentiment = self.nlp_processor.analyze_sentiment(user_input)
        sentiment_prefix = "¡Entiendo que estás preocupado! " if sentiment["compound"] < -0.1 else ""

        self.update_context(user_input)

        target_dept = self.context["department"] if self.context["department"] else department
        target_city = self.context["city"] if self.context["city"] else city

        intent = self.nlp_processor.classify_intent(user_input, self.intent_labels)

        if intent == "theoretical":
            questions = [self.normalize_text(q["question"]) for q in self.questions_data["theoretical"]]
            matches = get_close_matches(user_input_normalized, questions, n=1, cutoff=0.6)
            if matches:
                for q in self.questions_data["theoretical"]:
                    if self.normalize_text(q["question"]) == matches[0]:
                        return sentiment_prefix + q["answer"]

        dynamic_questions = [self.normalize_text(q["question"]) for q in self.questions_data["dynamic"]]
        matches = get_close_matches(user_input_normalized, dynamic_questions, n=1, cutoff=0.6)
        if matches:
            for q in self.questions_data["dynamic"]:
                if self.normalize_text(q["question"]) == matches[0]:
                    if q["type"] in ["weather", "weather_sowing_advice", "weather_forecast", "current_location", "irrigation_advice"]:
                        return sentiment_prefix + "Funcionalidad de clima y localización por implementar."
                    elif q["type"] == "recommendation":
                        if target_dept:
                            recommendations = self.dataset_processor.get_recommended_crops(target_dept)
                            if recommendations:
                                response = sentiment_prefix + f"En {target_dept.capitalize()}, te recomiendo los siguientes cultivos:\n"
                                for rec in recommendations:
                                    response += f"- {rec['crop']} con un rendimiento de {rec['yield']} ton/ha (año {rec['year']})\n"
                                return response
                        return sentiment_prefix + q["answer_template"]
                    elif q["type"] == "location_based_recommendation":
                        recommendations = self.dataset_processor.get_recommended_crops(target_dept)
                        if recommendations:
                            response = sentiment_prefix + f"En {target_dept.capitalize()}, te recomiendo los siguientes cultivos:\n"
                            for rec in recommendations:
                                response += f"- {rec['crop']} con un rendimiento de {rec['yield']} ton/ha (año {rec['year']})\n"
                            return response
                        return sentiment_prefix + "No identifico tu departamento o no tengo datos."
                    elif q["type"] == "crop_profitability":
                        crop = self.extract_crop(user_input)
                        if " o " in user_input_normalized:
                            crops = user_input_normalized.split(" o ")
                            crop1 = self.extract_crop(crops[0])
                            crop2 = self.extract_crop(crops[1])
                            if crop1 and crop2:
                                comparison = self.dataset_processor.compare_crops_profitability(crop1, crop2, target_dept)
                                if comparison:
                                    return sentiment_prefix + f"En {comparison['department']}, {comparison['best'].capitalize()} es más rentable: {comparison['crop1']} ({comparison['yield1']} ton/ha) vs {comparison['crop2']} ({comparison['yield2']} ton/ha)."
                                return sentiment_prefix + "No tengo datos suficientes para comparar esos cultivos."
                        if crop:
                            profitability = self.dataset_processor.get_most_favorable_department(crop)
                            if profitability:
                                return sentiment_prefix + q["answer_template"].format(
                                    crop=crop.capitalize(),
                                    department=profitability["department"],
                                    yield_value=profitability["value"]
                                )
                        return sentiment_prefix + "No identifico el cultivo o datos de rentabilidad."
                    elif q["type"] == "crop_production":
                        crop = self.extract_crop(user_input)
                        if crop:
                            if "menos" in user_input_normalized:
                                min_production = self.dataset_processor.get_least_favorable_department(crop, "Produccion (ton)")
                                if min_production:
                                    return sentiment_prefix + q["answer_template"].format(
                                        crop=crop.capitalize(),
                                        department=min_production["department"],
                                        production=min_production["value"]
                                    )
                            elif "más" in user_input_normalized:
                                max_production = self.dataset_processor.get_most_favorable_department(crop, "Produccion (ton)")
                                if max_production:
                                    return sentiment_prefix + q["answer_template"].format(
                                        crop=crop.capitalize(),
                                        department=max_production["department"],
                                        production=max_production["value"]
                                    )
                            elif target_dept:
                                dept_key = target_dept
                                recent_year = max(self.dataset_processor.datasets[dept_key]["Año"]) if dept_key in self.dataset_processor.datasets else 2020
                                production = self.dataset_processor.get_production_by_location(crop, target_dept, recent_year)
                                if production:
                                    return sentiment_prefix + q["answer_template"].format(
                                        crop=crop.capitalize(),
                                        department=production["location"],
                                        production=production["production_ton"]
                                    )
                        return sentiment_prefix + "No identifico el cultivo o datos de producción."
                    elif q["type"] == "crop_timing":
                        crop = self.extract_crop(user_input)
                        if crop:
                            crop_data = self.agricultural_data[self.agricultural_data["cultivo"].str.lower() == self.normalize_text(crop)]
                            if not crop_data.empty:
                                month = crop_data.iloc[0]["mes_siembra"]
                                return sentiment_prefix + q["answer_template"].format(crop=crop.capitalize(), month=month)
                            return sentiment_prefix + f"No tengo datos de {crop.capitalize()}. ¿Otro cultivo?"
                        return sentiment_prefix + "Especifica un cultivo (ej. 'maíz')."

        if intent == "least_favorable_department":
            crop = self.extract_crop(user_input)
            if crop:
                result = self.dataset_processor.get_least_favorable_department(crop)
                if result:
                    return sentiment_prefix + f"El departamento menos favorable para sembrar {crop.capitalize()} es {result['department']} con un rendimiento de {result['value']} ton/ha en {result['year']}."
                return sentiment_prefix + f"No tengo datos suficientes para determinar el departamento menos favorable para {crop.capitalize()}."
            return sentiment_prefix + "Especifica un cultivo (ej. 'maíz')."

        if intent == "recommended_crops":
            recommendations = self.dataset_processor.get_recommended_crops(target_dept)
            if recommendations:
                response = sentiment_prefix + f"En {target_dept.capitalize()}, te recomiendo los siguientes cultivos:\n"
                for rec in recommendations:
                    response += f"- {rec['crop']} con un rendimiento de {rec['yield']} ton/ha (año {rec['year']})\n"
                return response
            return sentiment_prefix + f"No tengo datos suficientes para recomendar cultivos en {target_dept.capitalize()}."

        if intent == "production_query":
            crop = self.extract_crop(user_input)
            year = self.extract_year(user_input)
            location = extract_location(user_input, self.department_data)
            location_key = location["city"] if location and location["city"] else (location["department"] if location else target_dept)
            location_type = "municipality" if location and location["city"] else "department"
            if crop and year and location_key:
                result = self.dataset_processor.get_production_by_location(crop, location_key, year, location_type)
                if result:
                    return sentiment_prefix + f"En {result['location']} ({result['location_type']}), se produjeron {result['production_ton']} toneladas de {result['crop']} en {result['year']}."
                return sentiment_prefix + f"No tengo datos de producción para {crop.capitalize()} en esa ubicación y año."
            return sentiment_prefix + "Especifica el cultivo, la ubicación y el año (ej. 'maíz en Manizales en 2020')."

        words = user_input.split()
        if not matches or len(words) > 6:
            return sentiment_prefix + self.call_external_api(user_input)

        return sentiment_prefix + "No entendí tu pregunta. ¿Más detalles o reformúlala?"