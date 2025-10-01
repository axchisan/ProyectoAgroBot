import pandas as pd
import requests
from typing import Optional, Dict

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
    "boyacá": {"city": "Tunja", "department": "Boyacá"},
    "guavatá": {"city": "Guavatá", "department": "Santander"},
    "santander": {"city": "Bucaramanga", "department": "Santander"}
}


def get_location_from_coords(lat: float, lon: float) -> Optional[Dict]:
    """
    Convierte coordenadas en ciudad y departamento usando Nominatim (OpenStreetMap).

    Args:
        lat (float): Latitud.
        lon (float): Longitud.

    Returns:
        Dict con city y department o None si falla.
    """
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lon, "format": "json", "addressdetails": 1}
    headers = {
        "User-Agent": "Agrobot/1.0 (contacto@agrobot.com)"  # Nominatim requiere un User-Agent
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        address = data.get("address", {})
        city = address.get("city") or address.get("town") or address.get("village")
        department = address.get("state")

        # Log para depuración
        print(
            f"Nominatim response: lat={lat}, lon={lon}, city={city}, department={department}, address={address}"
        )

        # Asegurarse de que la ubicación esté en Colombia
        if address.get("country_code") != "co":
            print(
                "Ubicación fuera de Colombia, country_code:",
                address.get("country_code"),
            )
            return None

        # Intentar mapear con LOCATION_DATA usando el departamento primero
        if department:
            dept_key = department.lower().strip()
            print(f"Buscando departamento: {dept_key}")
            if dept_key in LOCATION_DATA:
                print(
                    f"Departamento encontrado en LOCATION_DATA: {LOCATION_DATA[dept_key]}"
                )
                return LOCATION_DATA[dept_key]
            for key, value in LOCATION_DATA.items():
                if value["department"].lower().strip() == dept_key:
                    print(
                        f"Departamento encontrado en LOCATION_DATA (búsqueda inversa): {value}"
                    )
                    return value

        # Intentar mapear con LOCATION_DATA usando la ciudad
        if city:
            city_key = city.lower().strip()
            print(f"Buscando ciudad: {city_key}")
            if city_key in LOCATION_DATA:
                print(f"Ciudad encontrada en LOCATION_DATA: {LOCATION_DATA[city_key]}")
                return LOCATION_DATA[city_key]
            for key, value in LOCATION_DATA.items():
                if value["city"].lower().strip() == city_key:
                    print(
                        f"Ciudad encontrada en LOCATION_DATA (búsqueda inversa): {value}"
                    )
                    return value

        # Si no se encuentra en LOCATION_DATA, devolver lo que Nominatim proporcionó
        if city and department:
            print(
                f"No se encontró en LOCATION_DATA, devolviendo: city={city}, department={department}"
            )
            return {"city": city.capitalize(), "department": department.capitalize()}
        else:
            print("No se pudo determinar ciudad o departamento.")
            return None
    except requests.RequestException as e:
        print(f"Error al consultar Nominatim: {e}")
        return None


def extract_location(
    user_input: str, department_data: pd.DataFrame = None
) -> Optional[Dict]:
    """
    Extrae la ciudad o departamento del texto del usuario.

    Args:
        user_input (str): Entrada del usuario.
        department_data (pd.DataFrame, optional): DataFrame con datos de departamentos.

    Returns:
        Dict con city y department o None si no se encuentra.
    """
    user_input = user_input.lower()
    for location, data in LOCATION_DATA.items():
        if location in user_input:
            return data
    if department_data is not None and not department_data.empty:
        for dept in department_data["departamento"].str.lower().unique():
            if dept in user_input:
                return {"city": None, "department": dept.capitalize()}
    return None


def recommend_crop_by_location(
    department: str, department_data: pd.DataFrame
) -> Optional[Dict]:
    """
    Recomienda el cultivo más rentable para un departamento.

    Args:
        department (str): Nombre del departamento.
        department_data (pd.DataFrame): DataFrame con datos de departamentos.

    Returns:
        Dict con información del cultivo recomendado o None si no hay datos.
    """
    if department and not department_data.empty:
        dept_data = department_data[
            department_data["departamento"].str.lower() == department.lower()
        ]
        if not dept_data.empty:
            best_crop = dept_data.loc[dept_data["rendimiento_ton_ha"].idxmax()]
            return {
                "department": department.capitalize(),
                "crop": best_crop["cultivo_destacado"],
                "yield": best_crop["rendimiento_ton_ha"],
            }
    return None


def get_production_data(
    crop: str, department: str, department_data: pd.DataFrame
) -> Optional[Dict]:
    """
    Obtiene datos de producción para un cultivo en un departamento.

    Args:
        crop (str): Nombre del cultivo.
        department (str): Nombre del departamento.
        department_data (pd.DataFrame): DataFrame con datos de departamentos.

    Returns:
        Dict con datos de producción o None si no hay datos.
    """
    if crop and department and not department_data.empty:
        data = department_data[
            (department_data["cultivo_destacado"].str.lower() == crop.lower())
            & (department_data["departamento"].str.lower() == department.lower())
        ]
        if not data.empty:
            return {
                "crop": crop.capitalize(),
                "department": department.capitalize(),
                "production": (
                    data.iloc[0]["produccion_ton"]
                    if "produccion_ton" in data.columns
                    else 0
                ),
            }
    return None


def get_crop_profitability(crop: str, department_data: pd.DataFrame) -> Optional[Dict]:
    """
    Determina la rentabilidad de un cultivo buscando el departamento con mayor rendimiento.

    Args:
        crop (str): Nombre del cultivo.
        department_data (pd.DataFrame): DataFrame con datos de departamentos.

    Returns:
        Dict con información de rentabilidad o None si no hay datos.
    """
    if crop and not department_data.empty:
        data = department_data[
            department_data["cultivo_destacado"].str.lower() == crop.lower()
        ]
        if not data.empty:
            best_dept = data.loc[data["rendimiento_ton_ha"].idxmax()]
            return {
                "crop": crop.capitalize(),
                "department": best_dept["departamento"],
                "yield": best_dept["rendimiento_ton_ha"],
            }
    return None


def get_department_with_min_production(
    crop: str, department_data: pd.DataFrame
) -> Optional[Dict]:
    """
    Identifica el departamento con menor producción de un cultivo.

    Args:
        crop (str): Nombre del cultivo.
        department_data (pd.DataFrame): DataFrame con datos de departamentos.

    Returns:
        Dict con información del departamento o None si no hay datos.
    """
    if crop and not department_data.empty:
        data = department_data[
            department_data["cultivo_destacado"].str.lower() == crop.lower()
        ]
        if not data.empty and "produccion_ton" in data.columns:
            min_dept = data.loc[data["produccion_ton"].idxmin()]
            return {
                "crop": crop.capitalize(),
                "department": min_dept["departamento"],
                "production": min_dept["produccion_ton"],
            }
    return None


def get_department_with_max_production(
    crop: str, department_data: pd.DataFrame
) -> Optional[Dict]:
    """
    Identifica el departamento con mayor producción de un cultivo.

    Args:
        crop (str): Nombre del cultivo.
        department_data (pd.DataFrame): DataFrame con datos de departamentos.

    Returns:
        Dict con información del departamento o None si no hay datos.
    """
    if crop and not department_data.empty:
        data = department_data[
            department_data["cultivo_destacado"].str.lower() == crop.lower()
        ]
        if not data.empty and "produccion_ton" in data.columns:
            max_dept = data.loc[data["produccion_ton"].idxmax()]
            return {
                "crop": crop.capitalize(),
                "department": max_dept["departamento"],
                "production": max_dept["produccion_ton"],
            }
    return None
