import pickle
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Descargar recursos de NLTK
nltk.download('vader_lexicon')

class NLPProcessor:
    def __init__(self):
        # Cargar el modelo y el tokenizador
        self.tokenizer = AutoTokenizer.from_pretrained("app/models/intent_classifier")
        self.model = AutoModelForSequenceClassification.from_pretrained("app/models/intent_classifier")
        self.model.eval()
        # Cargar el label_map
        with open("app/models/intent_classifier/label_map.pkl", "rb") as f:
            self.label_map = pickle.load(f)
        self.reverse_label_map = {v: k for k, v in self.label_map.items()}
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def classify_intent(self, user_input: str, candidate_labels: list) -> str:
        # Tokenizar la entrada
        inputs = self.tokenizer(
            user_input,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128
        )
        print(f"Input tokenized for '{user_input}': {inputs}")  # Depuración

        # Hacer la predicción
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            predicted_label_id = torch.argmax(logits, dim=1).item()
            print(f"Logits: {logits}, Predicted ID: {predicted_label_id}")  # Depuración

        # Mapear el ID a la etiqueta
        predicted_label = self.reverse_label_map[predicted_label_id]
        print(f"Predicted label: {predicted_label}, Reverse map: {self.reverse_label_map}")  # Depuración
        return predicted_label

    def analyze_sentiment(self, user_input: str) -> dict:
        return self.sentiment_analyzer.polarity_scores(user_input)