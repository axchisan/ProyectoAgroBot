import pandas as pd # type: ignore
# Este archivo gestiona la lógica de ubicación y recomendaciones basadas en datos geográficos.


# Diccionario predefinido de ciudades y departamentos colombianos 
LOCATION_DATA = {
    "bogotá": {"city": "Bogotá", "department": "Cundinamarca"},
    "medellín": {"city": "Medellín", "department": "Antioquia"},
    "cali": {"city": "Cali", "department": "Valle del Cauca"},
    "barranquilla": {"city": "Barranquilla", "department": "Atlántico"},
    "cartagena": {"city": "Cartagena", "department": "Bolívar"},
    "pereira": {"city": "Pereira", "department": "Risaralda"},
    "bucaramanga": {"city": "Bucaramanga", "department": "Santander"},
    "manizales": {"city": "Manizales", "department": "Caldas"},
    "cúcuta": {"city": "Cúcuta", "department": "Norte de Santander"},
    "antioquia": {"city": "Medellín", "department": "Antioquia"},
    "cundinamarca": {"city": "Bogotá", "department": "Cundinamarca"},
    "valle del cauca": {"city": "Cali", "department": "Valle del Cauca"},
    "tolima": {"city": "Ibagué", "department": "Tolima"},
    "santander": {"city": "Bucaramanga", "department": "Santander"},
    "nariño": {"city": "Pasto", "department": "Nariño"},
    "huila": {"city": "Neiva", "department": "Huila"},
    "boyacá": {"city": "Tunja", "department": "Boyacá"}
}

def extract_location(user_input: str, department_data: pd.DataFrame = None) -> dict:
    # Extrae la ciudad o departamento del texto del usuario, buscando coincidencias en LOCATION_DATA o en department_data.
    # Retorna un diccionario con city y department o None si no se encuentra.
    user_input = user_input.lower()
    for location, data in LOCATION_DATA.items():
        if location in user_input:
            return data
    if department_data is not None and not department_data.empty:
        for dept in department_data["departamento"].str.lower().unique():
            if dept in user_input:
                return {"city": None, "department": dept}
    return None

def recommend_crop_by_location(department: str, department_data: pd.DataFrame) -> dict:
    # Recomienda el cultivo más rentable para un departamento basado en el rendimiento máximo.
    # Usamos pandas para filtrar y encontrar el cultivo con mayor rendimiento_ton_ha.
    if department and not department_data.empty:
        dept_data = department_data[department_data["departamento"].str.lower() == department.lower()]
        if not dept_data.empty:
            best_crop = dept_data.loc[dept_data["rendimiento_ton_ha"].idxmax()]
            return {
                "department": department.capitalize(),
                "crop": best_crop["cultivo_destacado"],
                "yield": best_crop["rendimiento_ton_ha"]
            }
    return None

def get_production_data(crop: str, department: str, department_data: pd.DataFrame) -> dict:
    # Obtiene datos de producción para un cultivo específico en un departamento.
    # Filtra department_data usando pandas y retorna producción en toneladas.
    if crop and department and not department_data.empty:
        data = department_data[
            (department_data["cultivo_destacado"].str.lower() == crop.lower()) &
            (department_data["departamento"].str.lower() == department.lower())
        ]
        if not data.empty:
            return {
                "crop": crop.capitalize(),
                "department": department.capitalize(),
                "production": data.iloc[0]["produccion_ton"] if "produccion_ton" in data.columns else 0
            }
    return None

def get_crop_profitability(crop: str, department_data: pd.DataFrame) -> dict:
    # Determina la rentabilidad de un cultivo buscando el departamento con mayor rendimiento.
    # Usa pandas para maximizar rendimiento_ton_ha.
    if crop and not department_data.empty:
        data = department_data[department_data["cultivo_destacado"].str.lower() == crop.lower()]
        if not data.empty:
            best_dept = data.loc[data["rendimiento_ton_ha"].idxmax()]
            return {
                "crop": crop.capitalize(),
                "department": best_dept["departamento"],
                "yield": best_dept["rendimiento_ton_ha"]
            }
    return None

def get_department_with_min_production(crop: str, department_data: pd.DataFrame) -> dict:
    # Identifica el departamento con menor producción de un cultivo.
    if crop and not department_data.empty:
        data = department_data[department_data["cultivo_destacado"].str.lower() == crop.lower()]
        if not data.empty and "produccion_ton" in data.columns:
            min_dept = data.loc[data["produccion_ton"].idxmin()]
            return {
                "crop": crop.capitalize(),
                "department": min_dept["departamento"],
                "production": min_dept["produccion_ton"]
            }
    return None

def get_department_with_max_production(crop: str, department_data: pd.DataFrame) -> dict:
    # Identifica el departamento con mayor producción de un cultivo.
    # con pandas se  maximiza produccion_ton
    if crop and not department_data.empty:
        data = department_data[department_data["cultivo_destacado"].str.lower() == crop.lower()]
        if not data.empty and "produccion_ton" in data.columns:
            max_dept = data.loc[data["produccion_ton"].idxmax()]
            return {
                "crop": crop.capitalize(),
                "department": max_dept["departamento"],
                "production": max_dept["produccion_ton"]
            }
    return None