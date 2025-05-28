import pandas as pd # type: ignore
import pickle
from sklearn.model_selection import train_test_split # type: ignore
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import torch # type: ignore
from torch.utils.data import Dataset # type: ignore
import re

def normalize_text(text: str) -> str:
    """Normaliza el texto eliminando puntuación y convirtiéndolo a minúsculas."""
    text = text.lower().strip()
    text = re.sub(r'[¿¡!?,.;]', '', text)
    return text

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

def train_intent_model(training_data, output_dir="app/models/intent_classifier"):
    """Entrena el modelo de clasificación de intenciones y lo guarda."""
    # Normalizar los datos de entrenamiento
    training_data = [(normalize_text(question), intent) for question, intent in training_data]

    # Convertir los datos a un DataFrame
    df = pd.DataFrame(training_data, columns=["question", "intent"])

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

    # Definir los argumentos de entrenamiento
    training_args = TrainingArguments(
        output_dir='./results', #eto guarda checkpoints los cuales se puede eliminar luego de haber entrenado el modelo
        num_train_epochs=15,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        warmup_steps=1000,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        learning_rate=2e-5,
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
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    # Guardar el label_map
    label_map = train_dataset.label_map
    with open(f"{output_dir}/label_map.pkl", "wb") as f:
        pickle.dump(label_map, f)

    print(f"Modelo entrenado y guardado en '{output_dir}'")