import pandas as pd # type: ignore
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer # type: ignore
from sklearn.linear_model import LogisticRegression # type: ignore
from sklearn.pipeline import make_pipeline # type: ignore

# Datos de entrenamiento (preguntas etiquetadas)
training_data = [
    ("¿Qué es Agrobot?", "theoretical"),
    ("¿Qué es la agroecología?", "theoretical"),
    ("¿Cuál es el clima en Bogotá?", "weather"),
    ("¿Qué cultivos son recomendables para mi región?", "recommendation"),
    ("¿Qué cultivo me recomiendas sembrar en Antioquia?", "location_based_recommendation"),
    ("¿Cuándo debo sembrar maíz?", "crop_timing"),
    ("¿Cómo puedo optimizar el riego?", "irrigation_advice"),
    ("¿Qué es la permacultura?", "theoretical"),
    ("¿Cuál es el pronóstico del tiempo?", "weather"),
    ("¿Qué debo sembrar en Cundinamarca?", "location_based_recommendation")
]

# Preparar datos
questions, labels = zip(*training_data)

# Crear un pipeline con vectorización y clasificación
pipeline = make_pipeline(TfidfVectorizer(), LogisticRegression())

# Entrenar el modelo
pipeline.fit(questions, labels)

# Guardar el modelo entrenado
with open("app/models/intent_classifier.pkl", "wb") as f:
    pickle.dump(pipeline, f)

print("Modelo entrenado y guardado como 'intent_classifier.pkl'")