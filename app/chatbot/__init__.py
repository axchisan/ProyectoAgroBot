from .data_loader import load_questions, load_agricultural_data, load_department_data
from .question_processor import QuestionProcessor

def init_chatbot():
    # Cargar datos
    questions_data = load_questions("data/questions.json")
    agricultural_data = load_agricultural_data("data/processed/crops_data.csv")
    department_data = load_department_data("data/raw/departments_data.csv")
    
    # API key de Cohere
    api_key = "rULZJwpsI3wUmnaJwDMGTqwRpDLvHbHoZZRURNLh"  # Reemplaza con tu clave API de Cohere
    
    # Inicializar el QuestionProcessor con la API key
    processor = QuestionProcessor(
        questions_data,
        agricultural_data,
        department_data,
        api_key=api_key,
        api_type="cohere"  # Usaremos la API de Cohere
    )
    return processor