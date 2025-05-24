from .data_loader import load_questions, load_agricultural_data, load_department_data
from .question_processor import QuestionProcessor

def init_chatbot():
    questions_data = load_questions("data/questions.json")
    agricultural_data = load_agricultural_data("data/processed/crops_data.csv")
    department_data = load_department_data("data/raw/departments_data.csv")
    processor = QuestionProcessor(questions_data, agricultural_data, department_data)
    return processor