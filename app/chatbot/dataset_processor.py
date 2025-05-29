import pandas as pd # type: ignore
import os
from typing import Dict, List, Optional

class DatasetProcessor:
    def __init__(self, data_dir: str = "data/processed"):
        # Inicializa el procesador con la ruta base de los datasets.
        # data_dir: Directorio raíz donde están las subcarpetas con los CSV.
        self.data_dir = data_dir
        self.datasets = self._load_all_datasets()

    def _load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        # carga dinámicamente todos los CSV en las subcarepetas de data_dir
        # Clave: Nombre del archivo sin extensión 
        # Valor: DataFrame con los datos del CSV.
        datasets = {}
        for root, _, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith(".csv"):
                    file_path = os.path.join(root, file)
                    # obtiene nombre del archivo sin la extensión para usarlo como clave
                    key = file.replace(".csv", "").lower()
                    try:
                        df = pd.read_csv(file_path)
                        datasets[key] = df
                    except Exception as e:
                        print(f"Error al cargar {file_path}: {e}")
        return datasets

    def get_least_favorable_department(self, crop: str, metric: str = "Rendimiento (ha/ton)") -> Optional[Dict]:
        # Encuentra el departamento menos favorable para un cultivo basado métrica.
        # crop es ombre del cultivo  maiz guayaba etc
        # metric: Columna para evaluar  "Rendimiento (ha/ton)"
        # Busca en los datasets de tipo 1 y 3 (por cultivo).
        crop_key = crop.lower()
        if crop_key in self.datasets:
            crop_data = self.datasets[crop_key]
            if not crop_data.empty and metric in crop_data.columns:
                # Filtra filas donde el rendimiento no sea 0 para evitar datos iincorrectos.
                valid_data = crop_data[crop_data[metric] > 0]
                if not valid_data.empty:
                    min_dept = valid_data.loc[valid_data[metric].idxmin()]
                    return {
                        "department": min_dept["Departamento"],
                        "value": min_dept[metric],
                        "year": min_dept["Año"]
                    }
        return None

    def get_recommended_crops(self, department: str, metric: str = "Rendimiento (ha/ton)") -> List[Dict]:
        # recomienda los mejores cultivos para un departamento basado en el mayor rendimiento.
        # metric columna para evaluar  Rendimiento (ha/ton)
        # Busca en el dataset del departamento (tipo 2)
        recommended = []
        dept_key = department.lower()
        if dept_key in self.datasets:
            dept_data = self.datasets[dept_key]
            if not dept_data.empty and metric in dept_data.columns:
                # Agrupa por producto y calcula el rendimiento promedio
                grouped = dept_data.groupby("Producto")[metric].mean().reset_index()
                # Ordena por rendimiento descendente y toma los mejores 3
                top_crops = grouped.sort_values(by=metric, ascending=False).head(3)
                for _, row in top_crops.iterrows():
                    # Obtiene el año más reciente para este cultivo
                    crop_data = dept_data[
                        (dept_data["Producto"].str.lower() == row["Producto"].lower()) &
                        (dept_data[metric] > 0)
                    ]
                    if not crop_data.empty:
                        recent_year = crop_data["Año"].max()
                        recommended.append({
                            "crop": row["Producto"].capitalize(),
                            "yield": row[metric],
                            "year": recent_year
                        })
        return recommended

    def get_production_by_location(self, crop: str, location: str, year: int, location_type: str = "department") -> Optional[Dict]:
        # obtenemos la producción de un cultivo en una ubicación específica (departamento o municipio) y año
        # year: Año específico  2020)
        # location_type: department o municipality para determinar qué dataset usar.
        crop = crop.lower()
        location = location.lower()

        if location_type == "department":
            # Usa datasets de tipo 2 (participación departamental)
            dept_key = location
            if dept_key in self.datasets:
                dept_data = self.datasets[dept_key]
                if not dept_data.empty:
                    data = dept_data[
                        (dept_data["Producto"].str.lower() == crop) &
                        (dept_data["Año"] == year)
                    ]
                    if not data.empty:
                        return {
                            "crop": crop.capitalize(),
                            "location": location.capitalize(),
                            "location_type": "department",
                            "production_ton": data["Produccion (ton)"].iloc[0],
                            "year": year
                        }
        elif location_type == "municipality":
            # Usa datasets de tipo 4 municipal, ejmplo tolima-cafe
            for key in self.datasets.keys():
                if key.endswith(f"-{crop}"):
                    dept_data = self.datasets[key]
                    if not dept_data.empty:
                        data = dept_data[
                            (dept_data["Municipio"].str.lower() == location) &
                            (dept_data["Año"] == year)
                        ]
                        if not data.empty:
                            return {
                                "crop": crop.capitalize(),
                                "location": location.capitalize(),
                                "location_type": "municipality",
                                "production_ton": data["Produccion (ton)"].iloc[0],
                                "year": year
                            }
        return None

    def get_average_yield_by_crop(self, crop: str) -> Optional[Dict]:
        # Calcula el rendimiento promedio de un cultivo a nivel nacional
        # Usa datasets de tipo 1 o 3 (por cultivo)
        crop_key = crop.lower()
        if crop_key in self.datasets:
            crop_data = self.datasets[crop_key]
            if not crop_data.empty and "Rendimiento (ha/ton)" in crop_data.columns:
                avg_yield = crop_data["Rendimiento (ha/ton)"].mean()
                return {
                    "crop": crop.capitalize(),
                    "average_yield": round(avg_yield, 2)
                }
        return None