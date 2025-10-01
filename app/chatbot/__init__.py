from .data_loader import load_questions, load_agricultural_data, load_department_data, load_dynamic_datasets
from .question_processor import QuestionProcessor
from .dataset_processor import DatasetProcessor
import os

def init_chatbot(weather_api_key=None, openai_api_key=None, questions_file="data/questions.json", agricultural_file="data/processed/Area_Produccion_y_Rendimiento_Nacional_por_Cultivo/Cafe.csv", department_file="data/raw/departments_data.csv", dynamic_data_dir="data/processed"):
    """
    Inicializa el chatbot con los datos necesarios.
    
    Args:
        weather_api_key (str, optional): Clave API para OpenWeatherMap.
        openai_api_key (str, optional): Clave API para OpenAI.
        questions_file (str): Ruta al archivo JSON de preguntas.
        agricultural_file (str): Ruta al archivo CSV de datos agrícolas.
        department_file (str): Ruta al archivo CSV de datos de departamentos.
        dynamic_data_dir (str): Directorio para cargar datasets dinámicos.
    
    Returns:
        QuestionProcessor: Instancia del procesador de preguntas.
    """
    # Cargar datos desde archivos
    questions_data = load_questions(questions_file)
    agricultural_data = load_agricultural_data(agricultural_file)
    department_data = load_department_data(department_file)
    dynamic_datasets = load_dynamic_datasets(dynamic_data_dir)
    
    # Obtener claves API desde variables de entorno si no se proporcionan
    weather_api_key = weather_api_key or os.getenv("OPENWEATHERMAP_API_KEY")
    openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY", "Api Key")  # Valor por defecto temporal
    
    # Inicializar DatasetProcessor con los datos dinámicos cargados
    dataset_processor = DatasetProcessor(dynamic_datasets)
    
    # Inicializar QuestionProcessor con las claves API y datos cargados
    processor = QuestionProcessor(
        questions_data=questions_data,
        agricultural_data=agricultural_data,
        department_data=department_data,
        dataset_processor=dataset_processor,
        weather_api_key=weather_api_key,
        api_key=openai_api_key,
        api_type="openai"
    )
    return processor