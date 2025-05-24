import pandas as pd # type: ignore
#Este archivo procesará la ubicación del usuario y buscará datos en el dataset de departamentos.
def extract_location(user_input: str, department_data: pd.DataFrame) -> str:
    user_input = user_input.lower()
    for dept in department_data["departamento"].str.lower().unique():
        if dept in user_input:
            return dept
    return None

def recommend_crop_by_location(department: str, department_data: pd.DataFrame) -> dict:
    if department:
        dept_data = department_data[department_data["departamento"].str.lower() == department.lower()]
        if not dept_data.empty:
            # Seleccionar el cultivo con mayor rendimiento
            best_crop = dept_data.loc[dept_data["rendimiento_ton_ha"].idxmax()]
            return {
                "department": department.capitalize(),
                "crop": best_crop["cultivo_destacado"],
                "yield": best_crop["rendimiento_ton_ha"]
            }
    return None