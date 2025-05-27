import pickle
import torch # type: ignore
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import nltk # type: ignore
from nltk.sentiment.vader import SentimentIntensityAnalyzer # type: ignore

nltk.download('vader_lexicon')

class NLPProcessor:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("app/models/intent_classifier")
        self.model = AutoModelForSequenceClassification.from_pretrained("app/models/intent_classifier")
        self.model.eval()
        with open("app/models/intent_classifier/label_map.pkl", "rb") as f:
            self.label_map = pickle.load(f)
        self.reverse_label_map = {v: k for k, v in self.label_map.items()}
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def classify_intent(self, user_input: str, candidate_labels: list) -> str:
        inputs = self.tokenizer(user_input, return_tensors="pt", padding=True, truncation=True, max_length=128)
        with torch.no_grad():
            outputs = self.model(**inputs)
            predicted_label_id = torch.argmax(outputs.logits, dim=1).item()
        predicted_label = self.reverse_label_map.get(predicted_label_id, "unknown")
        return predicted_label

    def analyze_sentiment(self, user_input: str) -> dict:
        return self.sentiment_analyzer.polarity_scores(user_input)