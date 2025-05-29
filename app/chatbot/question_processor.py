from difflib import get_close_matches
from typing import Dict, Optional
import pandas as pd # type: ignore
import requests # type: ignore
import re
from .weather_api import get_weather, get_weather_for_sowing
from .location_handler import (extract_location, recommend_crop_by_location, 
                              get_production_data, get_crop_profitability, 
                              get_department_with_min_production, get_department_with_max_production)
from .nlp_processor import NLPProcessor
from .dataset_processor import DatasetProcessor

# Este archivo es el núcleo del procesamiento de preguntas en Agrobot.
# - `difflib` compara similitudes de texto para encontrar coincidencias cercanas.
# - `pandas` maneja datos agrícolas y de departamentos.
# - `requests` realiza solicitudes a APIs externas (e.g., OpenAI, clima).
# - `re` se usa para normalizar texto eliminando puntuación.

class QuestionProcessor:
    def __init__(self, questions_data: Dict, agricultural_data: pd.DataFrame, department_data: pd.DataFrame, dataset_processor: DatasetProcessor, api_key: str = None, api_type: str = "openai"):
        # Inicializa el procesador con datos y configuración de API.
        # - `questions_data`: Diccionario con preguntas y respuestas.
        # - `agricultural_data`: DataFrame con datos de cultivos.
        # - `department_data`: DataFrame con datos de departamentos.
        # - `dataset_processor`: Instancia para manejar datasets dinámicos.
        # - `api_key`: Clave para la API de OpenAI; si no está, retorna un mensaje de error.
        # - `api_type`: Define el proveedor de la API (solo "openai" soportado aquí).
        # - `nlp_processor`: Instancia para análisis de texto.
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
            # Nuevas intenciones para preguntas dinámicas
            "least_favorable_department", "recommended_crops", "production_query"
        ]
        # Prompt inicial que guía a la API de OpenAI para generar respuestas contextuales.
        self.initial_prompt = (
            "Eres un complemento para el desarrollo de Agrobot, un chatbot colombiano diseñado para ayudar a pequeños agricultores. "
            "Tu rol es resolver preguntas que Agrobot no puede responder, ofreciendo conceptos, consejos y recomendaciones sobre cultivos, "
            "agricultura sostenible, manejo de plagas, y otros temas agrícolas relevantes para campesinos en Colombia. "
            "Responde siempre en español, de manera clara, práctica y adaptada al contexto colombiano, usando un lenguaje sencillo y amigable, usando como máximo 300 palabras. "
            "Si la pregunta es sobre técnicas agrícolas (como poda, siembra, recolección o manejo de plagas), proporciona pasos específicos, enumera las razones o beneficios, "
            "y asegura que la respuesta sea útil para un agricultor con conocimientos básicos. Cada respuesta debe tener al menos 150 palabras, "
            "evitando errores ortográficos o tipográficos. Ejemplo:\n"
            "Pregunta: ¿Qué técnicas de manejo de plagas recomiendas para el cultivo de tomate?\n"
            "Respuesta: Para el cultivo de tomate en Colombia, te recomiendo estas técnicas de manejo de plagas: "
            "1. **Uso de trampas amarillas:** Coloca trampas pegajosas amarillas para capturar insectos como la mosca blanca, común en tomate. "
            "2. **Rotación de cultivos:** Alterna el tomate con cultivos como maíz para romper el ciclo de plagas. "
            "3. **Control biológico:** Usa depredadores naturales como mariquitas para controlar áfidos. "
            "Estas técnicas son efectivas porque reducen las plagas sin depender solo de químicos, protegiendo el suelo y la salud del agricultor. Además, son económicas y fáciles de implementar en fincas pequeñas."
        )

    def normalize_text(self, text: str) -> str:
        # Normaliza el texto eliminando puntuación y convirtiéndolo a minúsculas para procesarlo uniformemente.
        text = text.lower().strip()
        text = re.sub(r'[¿¡!?,.;]', '', text)
        return text

    def extract_crop(self, user_input: str) -> str:
        # Extrae el nombre de un cultivo del texto del usuario de una lista predefinida.
        # Se puede expandir esta lista para incluir más cultivos según los datasets.
        crops = ["maíz", "papa", "café", "tomate", "arroz", "guayaba", "plátano", "cacao", "yuca", "caña de azúcar", "mora", "piña"]
        user_input = user_input.lower()
        for crop in crops:
            if crop in user_input:
                return crop
        return None

    def extract_year(self, user_input: str) -> Optional[int]:
        # Extrae un año del texto del usuario usando expresiones regulares.
        match = re.search(r'\b(20\d{2})\b', user_input)
        if match:
            return int(match.group(0))
        return None

    def call_external_api(self, user_input: str) -> str:
        # Llama a la API de OpenAI para procesar preguntas complejas o no cubiertas por las reglas internas.
        # Usa `requests` para enviar un payload con el prompt y el texto del usuario.
        # Configura el modelo `gpt-4o-mini` con `max_tokens=300` para limitar a 300 palabras.
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
                    "max_tokens": 300,  # Máximo de 300 palabras
                    "temperature": 0.3  # Nivel de precisión
                }
                print(f"Intentando llamar a {url} con payload: {payload}")
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()
                raw_response = response.json()["choices"][0]["message"]["content"].strip()
                # Corrección de tipeos (elimina letras duplicadas y espacios excesivos).
                raw_response = re.sub(r'\b(\w+)(\w)\2+\b', r'\1\2', raw_response)
                raw_response = re.sub(r'\s+', ' ', raw_response)
                return raw_response
            else:
                return "Tipo de API no soportado. Usa 'openai'."
        except requests.exceptions.HTTPError as e:
            return f"Error al consultar la API externa: {str(e)}. Verifica la URL, la clave API o los créditos."
        except requests.exceptions.RequestException as e:
            return f"Error de conexión con la API externa: {str(e)}. Revisa tu conexión o la configuración."
        except KeyError as e:
            return f"Error al procesar la respuesta de la API: {str(e)}. Revisa el formato de la respuesta."

    def process_question(self, user_input: str, city: str = "Bogotá", department: str = "Cundinamarca") -> str:
        # Procesa la pregunta del usuario, clasificando su intención y generando una respuesta.
        # Usa `nlp_processor` para analizar sentimiento e intención.
        # Maneja casos teóricos y dinámicos (clima, cultivos, datasets) con datos locales o la API.
        user_input_normalized = self.normalize_text(user_input)
        sentiment = self.nlp_processor.analyze_sentiment(user_input)
        sentiment_prefix = "¡Entiendo que estás preocupado! " if sentiment["compound"] < -0.1 else ""

        # Clasifica la intención de la pregunta usando el modelo NLP.
        intent = self.nlp_processor.classify_intent(user_input, self.intent_labels)
        print(f"Intención clasificada para '{user_input}': {intent}")

        # Procesar preguntas teóricas (respuestas predefinidas).
        if intent == "theoretical":
            questions = [self.normalize_text(q["question"]) for q in self.questions_data["theoretical"]]
            matches = get_close_matches(user_input_normalized, questions, n=1, cutoff=0.6)
            if matches:
                for q in self.questions_data["theoretical"]:
                    if self.normalize_text(q["question"]) == matches[0]:
                        return sentiment_prefix + q["answer"]

        # Procesar preguntas dinámicas (basadas en datos o clima).
        dynamic_questions = [self.normalize_text(q["question"]) for q in self.questions_data["dynamic"]]
        matches = get_close_matches(user_input_normalized, dynamic_questions, n=1, cutoff=0.6)
        if matches:
            for q in self.questions_data["dynamic"]:
                if self.normalize_text(q["question"]) == matches[0]:
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
                            return sentiment_prefix + "No pude obtener los datos climáticos."
                        elif q["type"] == "weather_sowing_advice":
                            weather_data = get_weather_for_sowing(target_city)
                            if weather_data:
                                return sentiment_prefix + q["answer_template"].format(
                                    city=target_city, description=weather_data["description"],
                                    temp=weather_data["temp"], humidity=weather_data["humidity"],
                                    recommendation=weather_data["recommendation"]
                                )
                            return sentiment_prefix + "No pude obtener datos para evaluar la siembra."
                    elif q["type"] == "weather_forecast":
                        return sentiment_prefix + q["answer_template"]
                    elif q["type"] == "current_location":
                        return sentiment_prefix + q["answer_template"].format(city=city, department=department)
                    elif q["type"] == "recommendation":
                        location = extract_location(user_input, self.department_data)
                        if location and location.get("department"):
                            recommendation = recommend_crop_by_location(location["department"], self.department_data)
                            if recommendation:
                                return sentiment_prefix + f"Te recomiendo sembrar {recommendation['crop']} en {location['department']} con un rendimiento de {recommendation['yield']} toneladas/ha."
                        return sentiment_prefix + q["answer_template"]
                    elif q["type"] == "location_based_recommendation":
                        target_dept = department
                        location = extract_location(user_input, self.department_data)
                        if location and location.get("department"):
                            target_dept = location["department"]
                        recommendation = recommend_crop_by_location(target_dept, self.department_data)
                        if recommendation and "crop" in recommendation and "yield" in recommendation:
                            return sentiment_prefix + q["answer_template"].format(
                                department=recommendation["department"], crop=recommendation["crop"],
                                yield_value=recommendation["yield"]
                            )
                        return sentiment_prefix + "No identifico tu departamento o no tengo datos."
                    elif q["type"] == "crop_profitability":
                        crop = self.extract_crop(user_input)
                        target_dept = extract_location(user_input, self.department_data)
                        if target_dept and target_dept.get("department"):
                            recommendation = recommend_crop_by_location(target_dept["department"], self.department_data)
                            if recommendation and "crop" in recommendation and "yield" in recommendation:
                                return sentiment_prefix + q["answer_template"].format(
                                    department=recommendation["department"], crop=recommendation["crop"],
                                    yield_value=recommendation["yield"]
                                )
                        elif crop:
                            profitability = get_crop_profitability(crop, self.department_data)
                            if profitability and "crop" in profitability and "yield" in profitability:
                                return sentiment_prefix + q["answer_template"].format(
                                    crop=profitability["crop"], department=profitability["department"],
                                    yield_value=profitability["yield"]
                                )
                        return sentiment_prefix + "No identifico el cultivo o datos de rentabilidad."
                    elif q["type"] == "crop_production":
                        crop = self.extract_crop(user_input)
                        target_dept = extract_location(user_input, self.department_data)
                        if target_dept and target_dept.get("department"):
                            production = get_production_data(crop, target_dept["department"], self.department_data)
                            if production and "production" in production:
                                return sentiment_prefix + q["answer_template"].format(
                                    crop=production["crop"], department=production["department"],
                                    production=production["production"]
                                )
                        elif "menos" in user_input:
                            min_production = get_department_with_min_production(crop, self.department_data)
                            if min_production and "production" in min_production:
                                return sentiment_prefix + q["answer_template"].format(
                                    crop=min_production["crop"], department=min_production["department"],
                                    production=min_production["production"]
                                )
                        elif "más" in user_input:
                            max_production = get_department_with_max_production(crop, self.department_data)
                            if max_production and "production" in max_production:
                                return sentiment_prefix + q["answer_template"].format(
                                    crop=max_production["crop"], department=max_production["department"],
                                    production=max_production["production"]
                                )
                        return sentiment_prefix + "No identifico el cultivo o datos de producción."
                    elif q["type"] == "crop_timing":
                        crop = self.extract_crop(user_input)
                        if crop:
                            crop_data = self.agricultural_data[self.agricultural_data["cultivo"].str.lower() == crop]
                            if not crop_data.empty:
                                month = crop_data.iloc[0]["mes_siembra"]
                                return sentiment_prefix + q["answer_template"].format(crop=crop, month=month)
                            return sentiment_prefix + f"No tengo datos de {crop}. ¿Otro cultivo?"
                        return sentiment_prefix + "Especifica un cultivo (ej. 'maíz')."
                    elif q["type"] == "irrigation_advice":
                        target_city = city
                        location = extract_location(user_input, self.department_data)
                        if location and location.get("city"):
                            target_city = location["city"]
                        weather_data = get_weather(target_city)
                        if weather_data and "main" in weather_data:
                            recommendation = "no se recomienda regar hoy" if weather_data["main"]["humidity"] > 60 else "puedes regar hoy"
                            return sentiment_prefix + q["answer_template"].format(city=target_city, recommendation=recommendation)
                        return sentiment_prefix + "No obtuve datos climáticos para riego."

        #  intenciones para preguntas dinámicas basadas en datasets
        if intent == "least_favorable_department":
            crop = self.extract_crop(user_input)
            if crop:
                result = self.dataset_processor.get_least_favorable_department(crop)
                if result:
                    return sentiment_prefix + f"El departamento menos favorable para sembrar {crop} es {result['department']} con un rendimiento de {result['value']} ton/ha en {result['year']}."
                return sentiment_prefix + f"No tengo datos suficientes para determinar el departamento menos favorable para {crop}."
            return sentiment_prefix + "Especifica un cultivo (ej. 'maíz')."

        if intent == "recommended_crops":
            location = extract_location(user_input, self.department_data)
            if location and location.get("department"):
                recommendations = self.dataset_processor.get_recommended_crops(location["department"])
                if recommendations:
                    response = sentiment_prefix + f"En {location['department']}, te recomiendo los siguientes cultivos:\n"
                    for rec in recommendations:
                        response += f"- {rec['crop']} con un rendimiento de {rec['yield']} ton/ha (año {rec['year']})\n"
                    return response
                return sentiment_prefix + f"No tengo datos suficientes para recomendar cultivos en {location['department']}."
            return sentiment_prefix + "Especifica tu departamento (ej. 'Santander')."

        if intent == "production_query":
            crop = self.extract_crop(user_input)
            year = self.extract_year(user_input)
            location = extract_location(user_input, self.department_data)
            if crop and year and location:
                # Primero intenta buscar como municipio
                result = self.dataset_processor.get_production_by_location(crop, location["city"] if location["city"] else location["department"], year, location_type="municipality")
                if result:
                    return sentiment_prefix + f"En {result['location']} ({result['location_type']}), se produjeron {result['production_ton']} toneladas de {result['crop']} en {result['year']}."
                # Si no encuentra como municipio, busca como departamento
                result = self.dataset_processor.get_production_by_location(crop, location["department"], year, location_type="department")
                if result:
                    return sentiment_prefix + f"En {result['location']} ({result['location_type']}), se produjeron {result['production_ton']} toneladas de {result['crop']} en {result['year']}."
                return sentiment_prefix + f"No tengo datos de producción para {crop} en esa ubicación y año."
            return sentiment_prefix + "Especifica el cultivo, la ubicación y el año (ej. 'maíz en Manizales en 2020')."

        # Si no hay coincidencias o la pregunta es compleja (>6 palabras), usa la API.
        words = user_input.split()
        if not matches or len(words) > 6:
            return sentiment_prefix + self.call_external_api(user_input)

        return sentiment_prefix + "No entendí tu pregunta. ¿Más detalles o reformúlala?"