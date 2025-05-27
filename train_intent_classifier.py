import pandas as pd # type: ignore
import pickle
from sklearn.model_selection import train_test_split # type: ignore
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import torch # type: ignore
from torch.utils.data import Dataset # type: ignore
import re

#normalizar txexto
def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[¿¡!?,.;]', '', text)  # Eliminar signos de puntuación
    return text

#  de entrenamiento con variaciones
training_data = [
    # Preguntas teóricas
    ("¿Qué es Agrobot?", "theoretical"),
    ("¿Q es Agrobot?", "theoretical"),
    ("¿Que es Agrobot?", "theoretical"),
    ("¿k es agrobot", "theoretical"),
    ("¿Qué significa Agrobot?", "theoretical"),
    ("¿Agrobot qué es?", "theoretical"),
    ("¿Qué es la agroecología?", "theoretical"),
    ("¿Q es agroecologia?", "theoretical"),
    ("¿Que es la agroecologia?", "theoretical"),
    ("¿Qué es agricultura sostenible?", "theoretical"),
    ("¿Q es agricultura sostenible?", "theoretical"),
    ("¿Agricultura sostenible qué es?", "theoretical"),
    ("¿Cómo controlo plagas orgánicas?", "theoretical"),
    ("¿Cómo puedo controlar plagas de manera orgánica?", "theoretical"),
    ("¿Q hago para plagas organicas?", "theoretical"),
    ("¿Qué es la rotación de cultivos?", "theoretical"),
    ("¿Q es rotacion cultivos?", "theoretical"),
    ("¿Rotación de cultivos qué es?", "theoretical"),
    ("¿Qué es la agricultura de precisión?", "theoretical"),
    ("¿Q es agricultura de precision?", "theoretical"),
    ("¿Cómo accedo a financiamiento agrícola?", "theoretical"),
    ("¿Cómo puedo acceder a financiamiento para mi proyecto agrícola?", "theoretical"),
    ("¿Q hago para financiar mi proyecto agricola?", "theoretical"),
    ("¿Qué es la agricultura regenerativa?", "theoretical"),
    ("¿Q es agricultura regenerativa?", "theoretical"),
    ("¿Qué es la agricultura urbana?", "theoretical"),
    ("¿Q es agricultura urbana?", "theoretical"),
    ("¿Agricultura urbana qué es?", "theoretical"),
    ("¿Qué es la permacultura?", "theoretical"),
    ("¿Q es permacultura?", "theoretical"),
    ("¿Permacultura qué significa?", "theoretical"),
    ("¿Qué son los cultivos transgénicos?", "theoretical"),
    ("¿Q son cultivos transgenicos?", "theoretical"),
    ("¿Qué es el manejo integrado de plagas?", "theoretical"),
    ("¿Q es manejo integrado plagas?", "theoretical"),
    ("¿Qué es la lixiviación de nutrientes?", "theoretical"),
    ("¿Q es lixiviacion nutrientes?", "theoretical"),
    ("¿Qué es la agricultura biodinámica?", "theoretical"),
    ("¿Q es agricultura biodinamica?", "theoretical"),
    ("¿Qué es la fertilidad del suelo?", "theoretical"),
    ("¿Q es fertilidad suelo?", "theoretical"),
    ("¿Qué es el monocultivo?", "theoretical"),
    ("¿Q es monocultivo?", "theoretical"),
    ("¿Qué es la agricultura de conservación?", "theoretical"),
    ("¿Q es agricultura conservacion?", "theoretical"),
    ("¿Qué son los biofertilizantes?", "theoretical"),
    ("¿Q son biofertilizantes?", "theoretical"),
    ("¿Qué es el pH del suelo y por qué es importante?", "theoretical"),
    ("¿Q es pH suelo?", "theoretical"),
    ("¿Por qué es importante el pH del suelo?", "theoretical"),
    ("¿Qué es la erosión del suelo?", "theoretical"),
    ("¿Q es erosion suelo?", "theoretical"),
    ("¿Cómo funciona la agricultura sostenible?", "theoretical"),
    ("¿Q funciona agricultura sostenible?", "theoretical"),
    ("¿Qué significa agroecología en la práctica?", "theoretical"),
    ("¿Q es agroecologia practica?", "theoretical"),
    ("¿Por qué es importante la rotación de cultivos?", "theoretical"),
    ("¿Por q rotacion cultivos?", "theoretical"),
    ("¿Cuáles son los beneficios de la permacultura?", "theoretical"),
    ("¿Beneficios permacultura?", "theoretical"),
    ("¿Qué impacto tienen los cultivos transgénicos?", "theoretical"),
    ("¿Q impacto cultivos transgenicos?", "theoretical"),
    ("¿Qué beneficios tiene la agroecología?", "theoretical"),
    ("¿Beneficios agroecologia?", "theoretical"),

    # Preguntas de clima (más variaciones)
    ("¿Cuál es el clima en Bogotá?", "weather"),
    ("¿Cual es el clima de Bogotá?", "weather"),
    ("¿Q clima hay en Bogotá?", "weather"),
    ("¿Clima en Bogotá?", "weather"),
    ("¿Cómo está el tiempo hoy en Medellín?", "weather"),
    ("¿Cmo esta tiempo Medellín?", "weather"),
    ("¿Tiempo hoy Medellín?", "weather"),
    ("¿Cuál es el pronóstico del tiempo?", "weather"),
    ("¿Q pronostico tiempo?", "weather"),
    ("¿Qué tiempo hace en Cali?", "weather"),
    ("¿Tiempo en Cali?", "weather"),
    ("¿Cómo consultar el clima?", "weather"),
    ("¿Cmo consulto clima?", "weather"),
    ("¿Cuál es el clima en mi ciudad?", "weather"),
    ("¿Clima mi ciudad?", "weather"),
    ("¿Qué clima hay en Pereira?", "weather"),
    ("¿Clima Pereira?", "weather"),
    ("¿Está lloviendo en Barranquilla?", "weather"),
    ("¿Llueve en Barranquilla?", "weather"),
    ("¿Cuál será el clima mañana en Bogotá?", "weather_forecast"),
    ("¿Clima mañana Bogotá?", "weather_forecast"),
    ("¿Hará sol mañana en Cartagena?", "weather_forecast"),
    ("¿Sol mañana Cartagena?", "weather_forecast"),
    ("¿Qué tiempo hará el fin de semana en Bucaramanga?", "weather_forecast"),
    ("¿Tiempo fin semana Bucaramanga?", "weather_forecast"),
    ("¿Cómo estará el clima la próxima semana en Manizales?", "weather_forecast"),
    ("¿Clima proxima semana Manizales?", "weather_forecast"),
    ("¿Habrá lluvia mañana en Cúcuta?", "weather_forecast"),
    ("¿Lluvia mañana Cúcuta?", "weather_forecast"),
    ("¿Cómo está el clima para sembrar en mi región?", "weather_sowing_advice"),
    ("¿Clima para sembrar región?", "weather_sowing_advice"),
    ("¿Es buen clima para sembrar en Bogotá?", "weather_sowing_advice"),
    ("¿Buen clima sembrar Bogotá?", "weather_sowing_advice"),
    ("¿El clima en Cali es adecuado para cultivar?", "weather_sowing_advice"),
    ("¿Clima Cali cultivar?", "weather_sowing_advice"),
    ("¿Qué tan húmedo está el clima en Medellín?", "weather_sowing_advice"),
    ("¿Humedad clima Medellín?", "weather_sowing_advice"),

    # Preguntas de ubicación
    ("¿Dónde estoy ubicado?", "current_location"),
    ("¿Donde estoy?", "current_location"),
    ("¿En qué ciudad estoy?", "current_location"),
    ("¿Ciudad donde estoy?", "current_location"),
    ("¿Cuál es mi ubicación actual?", "current_location"),
    ("¿Mi ubicacion?", "current_location"),
    ("¿Puedes decirme mi departamento?", "current_location"),
    ("¿Cual es mi departamento?", "current_location"),
    ("¿Estoy en Antioquia?", "current_location"),
    ("¿Estoy Antioquia?", "current_location"),
    ("¿Cuál es mi región?", "current_location"),
    ("¿Mi region?", "current_location"),
    ("¿Estoy en Santander?", "current_location"),
    ("¿Estoy en Cundinamarca?", "current_location"),

    # Preguntas de recomendación de cultivos
    ("¿Qué cultivos son recomendables para mi región?", "recommendation"),
    ("¿Q cultivos recomiendas región?", "recommendation"),
    ("¿Cultivos para mi region?", "recommendation"),
    ("¿Qué puedo sembrar en mi zona?", "recommendation"),
    ("¿Q siembro zona?", "recommendation"),
    ("¿Cuáles son los mejores cultivos para mi área?", "recommendation"),
    ("¿Mejores cultivos area?", "recommendation"),
    ("¿Qué cultivo me recomiendas para mi región?", "recommendation"),
    ("¿Cultivo recomiendas region?", "recommendation"),
    ("¿Qué cultivos crecen bien en mi departamento?", "recommendation"),
    ("¿Cultivos crecen departamento?", "recommendation"),
    ("¿Qué debería plantar en mi finca?", "recommendation"),
    ("¿Q plantar finca?", "recommendation"),
    ("¿Qué cultivo me recomiendas sembrar en Antioquia?", "location_based_recommendation"),
    ("¿Cultivo Antioquia?", "location_based_recommendation"),
    ("¿Qué debo sembrar en Cundinamarca?", "location_based_recommendation"),
    ("¿Sembrar Cundinamarca?", "location_based_recommendation"),
    ("¿Cuál es el mejor cultivo para Valle del Cauca?", "location_based_recommendation"),
    ("¿Mejor cultivo Valle Cauca?", "location_based_recommendation"),
    ("¿Qué cultivo es ideal para sembrar en Tolima?", "location_based_recommendation"),
    ("¿Cultivo ideal Tolima?", "location_based_recommendation"),
    ("¿Qué puedo plantar en Santander?", "location_based_recommendation"),
    ("¿Plantar Santander?", "location_based_recommendation"),
    ("¿Qué cultivo recomiendas para Nariño?", "location_based_recommendation"),
    ("¿Cultivo Nariño?", "location_based_recommendation"),
    ("¿Qué es bueno sembrar en Huila?", "location_based_recommendation"),
    ("¿Sembrar Huila?", "location_based_recommendation"),
    ("¿Qué cultivo tiene mejor rendimiento en Boyacá?", "location_based_recommendation"),
    ("¿Cultivo rendimiento Boyacá?", "location_based_recommendation"),
    ("¿Qué cultivo es más rentable en Antioquia?", "crop_profitability"),
    ("¿Cultivo rentable Antioquia?", "crop_profitability"),
    ("¿En qué departamento es más rentable sembrar guayaba?", "crop_profitability"),
    ("¿Rentable guayaba departamento?", "crop_profitability"),
    ("¿Dónde es más rentable plantar café?", "crop_profitability"),
    ("¿Rentable café donde?", "crop_profitability"),
    ("¿Qué cultivo genera más ganancias en Valle del Cauca?", "crop_profitability"),
    ("¿Ganancias Valle Cauca?", "crop_profitability"),
    ("¿Cuál es el cultivo más rentable en Cundinamarca?", "crop_profitability"),
    ("¿Cultivo rentable Cundinamarca?", "crop_profitability"),
    ("¿Qué cultivo tiene el mayor rendimiento en Valle del Cauca?", "crop_profitability"),
    ("¿Mayor rendimiento Valle Cauca?", "crop_profitability"),
    ("¿Dónde es más rentable sembrar tomate?", "crop_profitability"),
    ("¿Rentable tomate donde?", "crop_profitability"),
    ("¿Qué cultivo da más ganancias en Boyacá?", "crop_profitability"),
    ("¿Ganancias Boyacá?", "crop_profitability"),
    ("¿En qué departamento es mejor sembrar plátano?", "crop_profitability"),
    ("¿Mejor plátano departamento?", "crop_profitability"),
    ("¿Dónde obtengo más rendimiento con maíz?", "crop_profitability"),
    ("¿Rendimiento maíz donde?", "crop_profitability"),

    # Preguntas de producción
    ("¿En qué departamento se produce menos maíz?", "crop_production"),
    ("¿Donde producen menos maíz?", "crop_production"),
    ("¿Dónde se produce más café?", "crop_production"),
    ("¿Donde producen más café?", "crop_production"),
    ("¿Cuál es la producción de tomate en Cundinamarca?", "crop_production"),
    ("¿Producción tomate Cundinamarca?", "crop_production"),
    ("¿Qué departamento produce más arroz?", "crop_production"),
    ("¿Donde producen más arroz?", "crop_production"),
    ("¿Dónde se cultiva menos papa?", "crop_production"),
    ("¿Donde cultivan menos papa?", "crop_production"),
    ("¿Cuánto maíz se produce en Antioquia?", "crop_production"),
    ("¿Producción maíz Antioquia?", "crop_production"),
    ("¿Qué departamento produce más cacao?", "crop_production"),
    ("¿Donde producen más cacao?", "crop_production"),
    ("¿Dónde se produce menos plátano?", "crop_production"),
    ("¿Donde producen menos plátano?", "crop_production"),
    ("¿Cuál es la producción de guayaba en Valle del Cauca?", "crop_production"),
    ("¿Producción guayaba Valle Cauca?", "crop_production"),
    ("¿Qué departamento tiene la mayor producción de caña de azúcar?", "crop_production"),
    ("¿Mayor producción caña azúcar?", "crop_production"),
    ("¿Cuánto café se produce en Huila?", "crop_production"),
    ("¿Producción café Huila?", "crop_production"),
    ("¿Dónde se produce más yuca?", "crop_production"),
    ("¿Donde producen más yuca?", "crop_production"),
    ("¿Cuál es la producción de papa en Boyacá?", "crop_production"),
    ("¿Producción papa Boyacá?", "crop_production"),
    ("¿Qué departamento produce menos tomate?", "crop_production"),
    ("¿Donde producen menos tomate?", "crop_production"),

    # Preguntas de tiempo de siembra
    ("¿Cuándo debo sembrar maíz?", "crop_timing"),
    ("¿Cundo siembro maíz?", "crop_timing"),
    ("¿Cuál es el mejor momento para sembrar papa?", "crop_timing"),
    ("¿Mejor momento papa?", "crop_timing"),
    ("¿En qué mes debo plantar café?", "crop_timing"),
    ("¿Mes plantar café?", "crop_timing"),
    ("¿Cuándo es buena época para sembrar tomate?", "crop_timing"),
    ("¿Época tomate?", "crop_timing"),
    ("¿Cuál es el mejor mes para sembrar arroz?", "crop_timing"),
    ("¿Mejor mes arroz?", "crop_timing"),
    ("¿En qué mes se siembra guayaba?", "crop_timing"),
    ("¿Mes guayaba?", "crop_timing"),
    ("¿Cuándo debería plantar plátano?", "crop_timing"),
    ("¿Cundo plantar plátano?", "crop_timing"),
    ("¿Cuál es la mejor época para sembrar cacao?", "crop_timing"),
    ("¿Época cacao?", "crop_timing"),
    ("¿En qué momento debo sembrar yuca?", "crop_timing"),
    ("¿Momento yuca?", "crop_timing"),
    ("¿Cuándo es ideal sembrar caña de azúcar?", "crop_timing"),
    ("¿Ideal caña azúcar?", "crop_timing"),

    # Preguntas de riego
    ("¿Cómo puedo optimizar el riego?", "irrigation_advice"),
    ("¿Cmo optimizo riego?", "irrigation_advice"),
    ("¿Qué debo hacer para mejorar el riego en mi finca?", "irrigation_advice"),
    ("¿Q hago riego finca?", "irrigation_advice"),
    ("¿Cómo regar mis cultivos de manera eficiente?", "irrigation_advice"),
    ("¿Cmo regar eficiente?", "irrigation_advice"),
    ("¿Es un buen momento para regar en mi región?", "irrigation_advice"),
    ("¿Buen momento regar región?", "irrigation_advice"),
    ("¿Cómo afecta el clima al riego en mi zona?", "irrigation_advice"),
    ("¿Clima afecta riego?", "irrigation_advice"),
    ("¿Debo regar hoy en Bogotá?", "irrigation_advice"),
    ("¿Regar hoy Bogotá?", "irrigation_advice"),
    ("¿Cómo optimizo el agua para mis cultivos?", "irrigation_advice"),
    ("¿Optimizo agua cultivos?", "irrigation_advice"),
    ("¿Qué sistema de riego es mejor para mi finca?", "irrigation_advice"),
    ("¿Sistema riego finca?", "irrigation_advice"),
]

# Normalizar los datos de entrenamiento
training_data = [(normalize_text(question), intent) for question, intent in training_data]

# Convertir los datos a un DataFrame
df = pd.DataFrame(training_data, columns=["question", "intent"])

# Crear un dataset personalizado para Hugging Face
class IntentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.label_map = {label: idx for idx, label in enumerate(sorted(set(labels)))}

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]

        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(self.label_map[label], dtype=torch.long)
        }

# Preparar los datos
texts = df["question"].values
labels = df["intent"].values

# Dividir en entrenamiento y validación
train_texts, val_texts, train_labels, val_labels = train_test_split(texts, labels, test_size=0.2, random_state=42)

# Cargar el tokenizador y el modelo preentrenado en español
tokenizer = AutoTokenizer.from_pretrained('dccuchile/bert-base-spanish-wwm-uncased')
model = AutoModelForSequenceClassification.from_pretrained('dccuchile/bert-base-spanish-wwm-uncased', num_labels=len(set(labels)))

# Crear los datasets
train_dataset = IntentDataset(train_texts, train_labels, tokenizer)
val_dataset = IntentDataset(val_texts, val_labels, tokenizer)

# Definir los argumentos de entrenamiento (optimizados)
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=10,  # Aumentamos a 10 para mejor convergencia
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    warmup_steps=1000,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    learning_rate=2e-5,  # Ajuste de tasa de aprendizaje
)

# Crear el entrenador
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=lambda p: {"accuracy": (p.predictions.argmax(-1) == p.label_ids).mean()}
)

# Entrenar el modelo
trainer.train()

# Guardar el modelo y el tokenizador
model.save_pretrained("app/models/intent_classifier")
tokenizer.save_pretrained("app/models/intent_classifier")

# Guardar también un archivo .pkl con el label_map
label_map = train_dataset.label_map
with open("app/models/intent_classifier/label_map.pkl", "wb") as f:
    pickle.dump(label_map, f)

print("Modelo entrenado y guardado en 'app/models/intent_classifier'")