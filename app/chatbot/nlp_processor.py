import pickle
import nltk # type: ignore
from nltk.sentiment.vader import SentimentIntensityAnalyzer # type: ignore

# Descargar recursos de NLTK
nltk.download('vader_lexicon')

class NLPProcessor:
    def __init__(self):
        # Cargar el modelo entrenado
        with open("app/models/intent_classifier.pkl", "rb") as f:
            self.intent_classifier = pickle.load(f)
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def classify_intent(self, user_input: str, candidate_labels: list) -> str:
        return self.intent_classifier.predict([user_input])[0]

    def analyze_sentiment(self, user_input: str) -> dict:
        return self.sentiment_analyzer.polarity_scores(user_input)