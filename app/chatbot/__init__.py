from .data_loader import load_questions, load_agricultural_data, load_department_data, load_dynamic_datasets
from .question_processor import QuestionProcessor
from .dataset_processor import DatasetProcessor

def init_chatbot():
    # Carga los datos iniciales necesarios para el funcionamiento de Agrobot.
    # - `load_questions` lee un archivo JSON con preguntas teóricas y dinámicas.
    # - `load_agricultural_data` carga un CSV con datos agrícolas (cultivos, meses de siembra, etc.).
    # - `load_department_data` carga un CSV con datos de departamentos colombianos (producción, rendimiento).
    # - `load_dynamic_datasets` carga todos los CSV de las subcarpetas de data/processed.
    questions_data = load_questions("data/questions.json")
    agricultural_data = load_agricultural_data("data/processed/crops_data.csv")
    department_data = load_department_data("data/raw/departments_data.csv")
    dynamic_datasets = load_dynamic_datasets("data/processed")
    
    # Configura la API de OpenAI 
    api_key = "Aca poner la api key de OpenAI"
    
    # Inicializa el procesador de datasets con los datos dinámicos cargados.
    dataset_processor = DatasetProcessor()
    
    # Inicializa el procesador de preguntas con los datos cargados y la configuración de la API.
    processor = QuestionProcessor(
        questions_data,
        agricultural_data,
        department_data,
        dataset_processor,
        api_key=api_key,
        api_type="openai"
    )
    return processor