import pandas as pd
import os
from typing import Dict, List, Optional, Tuple
from unidecode import unidecode

class DatasetProcessor:
    def __init__(self, data_dir: str = "data/processed"):
        self.data_dir = data_dir
        self.crop_mappings = {
            "maiz": "maíz", "cafe": "café", "platano": "plátano", "guayaba manzana": "guayaba",
            "guayaba pera": "guayaba", "cana azucarera": "caña de azúcar", "cana panelera": "caña de azúcar"
        }
        self.datasets = self._load_all_datasets()

    def _normalize_name(self, name: str) -> str:
        # Normaliza nombres de cultivos y departamentos
        name = unidecode(name.lower().strip())
        return self.crop_mappings.get(name, name)

    def _load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        datasets = {}
        for root, _, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith(".csv"):
                    file_path = os.path.join(root, file)
                    key = file.replace(".csv", "").lower()
                    try:
                        df = pd.read_csv(file_path)
                        # Normalizar nombres de columnas
                        df.columns = [col.strip() for col in df.columns]
                        # Normalizar datos de cultivos y departamentos
                        if "Producto" in df.columns:
                            df["Producto"] = df["Producto"].apply(self._normalize_name)
                        if "Departamento" in df.columns:
                            df["Departamento"] = df["Departamento"].apply(self._normalize_name)
                        if "Municipio" in df.columns:
                            df["Municipio"] = df["Municipio"].apply(self._normalize_name)
                        datasets[key] = df
                    except Exception as e:
                        print(f"Error al cargar {file_path}: {e}")
        return datasets

    def get_least_favorable_department(self, crop: str, metric: str = "Rendimiento (ha/ton)") -> Optional[Dict]:
        crop = self._normalize_name(crop)
        # Buscar en datasets tipo 1 y 3 (por cultivo)
        crop_key = crop
        for key in self.datasets.keys():
            if key == crop or key.endswith(f"-{crop}"):
                crop_data = self.datasets[key]
                if not crop_data.empty and metric in crop_data.columns:
                    valid_data = crop_data[(crop_data[metric] > 0) & (crop_data[metric].notna())]
                    if not valid_data.empty:
                        min_dept = valid_data.loc[valid_data[metric].idxmin()]
                        return {
                            "department": min_dept["Departamento"].capitalize(),
                            "value": round(min_dept[metric], 2),
                            "year": min_dept["Año"]
                        }
        # Buscar en datasets tipo 2 (participación departamental)
        for key in self.datasets.keys():
            if not key.endswith("-" + crop):  # Evitar datasets municipales
                dept_data = self.datasets[key]
                if not dept_data.empty and "Producto" in dept_data.columns:
                    crop_data = dept_data[dept_data["Producto"] == crop]
                    if not crop_data.empty and metric in crop_data.columns:
                        valid_data = crop_data[(crop_data[metric] > 0) & (crop_data[metric].notna())]
                        if not valid_data.empty:
                            min_dept = valid_data.loc[valid_data[metric].idxmin()]
                            return {
                                "department": min_dept["Departamento"].capitalize(),
                                "value": round(min_dept[metric], 2),
                                "year": min_dept["Año"]
                            }
        return None

    def get_most_favorable_department(self, crop: str, metric: str = "Rendimiento (ha/ton)") -> Optional[Dict]:
        crop = self._normalize_name(crop)
        # Buscar en datasets tipo 1 y 3 (por cultivo)
        crop_key = crop
        for key in self.datasets.keys():
            if key == crop or key.endswith(f"-{crop}"):
                crop_data = self.datasets[key]
                if not crop_data.empty and metric in crop_data.columns:
                    valid_data = crop_data[(crop_data[metric] > 0) & (crop_data[metric].notna())]
                    if not valid_data.empty:
                        max_dept = valid_data.loc[valid_data[metric].idxmax()]
                        return {
                            "department": max_dept["Departamento"].capitalize(),
                            "value": round(max_dept[metric], 2),
                            "year": max_dept["Año"]
                        }
        # Buscar en datasets tipo 2 (participación departamental)
        for key in self.datasets.keys():
            if not key.endswith("-" + crop):
                dept_data = self.datasets[key]
                if not dept_data.empty and "Producto" in dept_data.columns:
                    crop_data = dept_data[dept_data["Producto"] == crop]
                    if not crop_data.empty and metric in crop_data.columns:
                        valid_data = crop_data[(crop_data[metric] > 0) & (crop_data[metric].notna())]
                        if not valid_data.empty:
                            max_dept = valid_data.loc[valid_data[metric].idxmax()]
                            return {
                                "department": max_dept["Departamento"].capitalize(),
                                "value": round(max_dept[metric], 2),
                                "year": max_dept["Año"]
                            }
        return None

    def get_recommended_crops(self, department: str, metric: str = "Rendimiento (ha/ton)") -> List[Dict]:
        department = self._normalize_name(department)
        recommended = []
        dept_key = department
        if dept_key in self.datasets:
            dept_data = self.datasets[dept_key]
            if not dept_data.empty and metric in dept_data.columns:
                grouped = dept_data.groupby("Producto")[metric].mean().reset_index()
                valid_grouped = grouped[(grouped[metric] > 0) & (grouped[metric].notna())]
                if not valid_grouped.empty:
                    top_crops = valid_grouped.sort_values(by=metric, ascending=False).head(3)
                    for _, row in top_crops.iterrows():
                        crop_data = dept_data[
                            (dept_data["Producto"] == row["Producto"]) &
                            (dept_data[metric] > 0)
                        ]
                        if not crop_data.empty:
                            recent_year = crop_data["Año"].max()
                            recommended.append({
                                "crop": row["Producto"].capitalize(),
                                "yield": round(row[metric], 2),
                                "year": recent_year
                            })
        return recommended

    def get_production_by_location(self, crop: str, location: str, year: int, location_type: str = "department") -> Optional[Dict]:
        crop = self._normalize_name(crop)
        location = self._normalize_name(location)

        if location_type == "department":
            dept_key = location
            if dept_key in self.datasets:
                dept_data = self.datasets[dept_key]
                if not dept_data.empty:
                    data = dept_data[
                        (dept_data["Producto"] == crop) &
                        (dept_data["Año"] == year) &
                        (dept_data["Produccion (ton)"] > 0)
                    ]
                    if not data.empty:
                        return {
                            "crop": crop.capitalize(),
                            "location": location.capitalize(),
                            "location_type": "department",
                            "production_ton": round(data["Produccion (ton)"].iloc[0], 2),
                            "year": year
                        }
        elif location_type == "municipality":
            for key in self.datasets.keys():
                if key.endswith(f"-{crop}"):
                    dept_data = self.datasets[key]
                    if not dept_data.empty:
                        data = dept_data[
                            (dept_data["Municipio"] == location) &
                            (dept_data["Año"] == year) &
                            (dept_data["Produccion (ton)"] > 0)
                        ]
                        if not data.empty:
                            return {
                                "crop": crop.capitalize(),
                                "location": location.capitalize(),
                                "location_type": "municipality",
                                "production_ton": round(data["Produccion (ton)"].iloc[0], 2),
                                "year": year
                            }
        return None

    def get_average_yield_by_crop(self, crop: str) -> Optional[Dict]:
        crop = self._normalize_name(crop)
        crop_key = crop
        for key in self.datasets.keys():
            if key == crop_key:
                crop_data = self.datasets[key]
                if not crop_data.empty and "Rendimiento (ha/ton)" in crop_data.columns:
                    valid_data = crop_data[(crop_data["Rendimiento (ha/ton)"] > 0) & (crop_data["Rendimiento (ha/ton)"].notna())]
                    if not valid_data.empty:
                        avg_yield = valid_data["Rendimiento (ha/ton)"].mean()
                        return {
                            "crop": crop.capitalize(),
                            "average_yield": round(avg_yield, 2)
                        }
        return None

    def compare_crops_profitability(self, crop1: str, crop2: str, department: Optional[str] = None) -> Optional[Dict]:
        crop1 = self._normalize_name(crop1)
        crop2 = self._normalize_name(crop2)
        if department:
            department = self._normalize_name(department)
            dept_key = department
            if dept_key in self.datasets:
                dept_data = self.datasets[dept_key]
                if not dept_data.empty:
                    crop1_data = dept_data[
                        (dept_data["Producto"] == crop1) &
                        (dept_data["Rendimiento (ha/ton)"] > 0)
                    ]
                    crop2_data = dept_data[
                        (dept_data["Producto"] == crop2) &
                        (dept_data["Rendimiento (ha/ton)"] > 0)
                    ]
                    if not crop1_data.empty and not crop2_data.empty:
                        avg_yield1 = crop1_data["Rendimiento (ha/ton)"].mean()
                        avg_yield2 = crop2_data["Rendimiento (ha/ton)"].mean()
                        return {
                            "crop1": crop1.capitalize(),
                            "yield1": round(avg_yield1, 2),
                            "crop2": crop2.capitalize(),
                            "yield2": round(avg_yield2, 2),
                            "department": department.capitalize(),
                            "best": crop1 if avg_yield1 > avg_yield2 else crop2
                        }
        else:
            # Comparar a nivel nacional
            crop1_yield = self.get_average_yield_by_crop(crop1)
            crop2_yield = self.get_average_yield_by_crop(crop2)
            if crop1_yield and crop2_yield:
                return {
                    "crop1": crop1.capitalize(),
                    "yield1": crop1_yield["average_yield"],
                    "crop2": crop2.capitalize(),
                    "yield2": crop2_yield["average_yield"],
                    "department": "nacional",
                    "best": crop1 if crop1_yield["average_yield"] > crop2_yield["average_yield"] else crop2
                }
        return None