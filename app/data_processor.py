import pandas as pd # type: ignore
import os
import json
from typing import Dict, List, Optional, Any
import glob

class DataProcessor:
    """Procesador modular de datos agrícolas"""
    
    def __init__(self, data_path: str = "data/processed"):
        self.data_path = data_path
        self.datasets = {}
        self.metadata = {}
        self._load_datasets()
    
    def _load_datasets(self):
        """Carga todos los datasets disponibles"""
        try:
            # Cargar datos nacionales por cultivo
            self._load_national_crop_data()
            
            # Cargar datos municipales por departamento
            self._load_municipal_data()
            
            # Cargar datos comparativos departamentales
            self._load_comparative_data()
            
            # Cargar datos de participación departamental
            self._load_departmental_participation()
            
            print(f"✅ Datasets cargados exitosamente: {len(self.datasets)} categorías")
            
        except Exception as e:
            print(f"❌ Error cargando datasets: {e}")
    
    def _load_national_crop_data(self):
        """Carga datos nacionales por cultivo"""
        path = os.path.join(self.data_path, "Area_Produccion_y_Rendimiento_Nacional_por_Cultivo")
        if os.path.exists(path):
            files = glob.glob(os.path.join(path, "*.csv"))
            self.datasets['national_crops'] = {}
            
            for file in files:
                crop_name = os.path.basename(file).replace('.csv', '')
                try:
                    df = pd.read_csv(file)
                    self.datasets['national_crops'][crop_name] = df
                except Exception as e:
                    print(f"Error cargando {file}: {e}")
            
            self.metadata['national_crops'] = {
                'description': 'Datos nacionales de área, producción y rendimiento por cultivo',
                'columns': ['Año', 'Departamento', 'Producto', 'Area (ha)', 'Produccion (ton)', 'Rendimiento (ha/ton)', 'Produccion Nacional (ton)', 'Area Nacional (ha)'],
                'count': len(self.datasets['national_crops'])
            }
    
    def _load_municipal_data(self):
        """Carga datos municipales por departamento y cultivo"""
        path = os.path.join(self.data_path, "Área_Producción,_Rendimiento_y_Participación_Municipal_en_el_Departamento_por_Cultivo")
        if os.path.exists(path):
            files = glob.glob(os.path.join(path, "*.csv"))
            self.datasets['municipal'] = {}
            
            for file in files:
                file_name = os.path.basename(file).replace('.csv', '')
                try:
                    df = pd.read_csv(file)
                    self.datasets['municipal'][file_name] = df
                except Exception as e:
                    print(f"Error cargando {file}: {e}")
            
            self.metadata['municipal'] = {
                'description': 'Datos municipales de área, producción y rendimiento por departamento y cultivo',
                'columns': ['Año', 'Municipio', 'Area Sembrada', 'Area Cosechada', 'Produccion (ton)', 'Rendimiento (ha/ton)'],
                'count': len(self.datasets['municipal'])
            }
    
    def _load_comparative_data(self):
        """Carga datos comparativos departamentales"""
        path = os.path.join(self.data_path, "Comparativo_de_Área,_Producción,_Rendimiento_y_Participación_Departamental_por_Cultivo.")
        if os.path.exists(path):
            files = glob.glob(os.path.join(path, "*.csv"))
            self.datasets['comparative'] = {}
            
            for file in files:
                file_name = os.path.basename(file).replace('.csv', '')
                try:
                    df = pd.read_csv(file)
                    self.datasets['comparative'][file_name] = df
                except Exception as e:
                    print(f"Error cargando {file}: {e}")
            
            self.metadata['comparative'] = {
                'description': 'Datos comparativos departamentales por cultivo',
                'columns': ['Año', 'Departamento', 'Producto', 'Area (ha)', 'Produccion (ton)', 'Rendimiento (ha/ton)', 'Produccion Nacional (ton)', 'Area Nacional (ha)'],
                'count': len(self.datasets['comparative'])
            }
    
    def _load_departmental_participation(self):
        """Carga datos de participación departamental"""
        path = os.path.join(self.data_path, "Participación_Departamental_en_la_Producción_y_en_el_Área_Cosechada")
        if os.path.exists(path):
            files = glob.glob(os.path.join(path, "*.csv"))
            self.datasets['departmental'] = {}
            
            for file in files:
                dept_name = os.path.basename(file).replace('.csv', '')
                try:
                    df = pd.read_csv(file)
                    self.datasets['departmental'][dept_name] = df
                except Exception as e:
                    print(f"Error cargando {file}: {e}")
            
            self.metadata['departmental'] = {
                'description': 'Participación departamental en producción y área cosechada',
                'columns': ['Departamento', 'Producto', 'Año', 'Area (ha)', 'Produccion (ton)', 'Rendimiento (ha/ton)'],
                'count': len(self.datasets['departmental'])
            }
    
    def get_available_datasets(self) -> Dict[str, Any]:
        """Retorna información sobre datasets disponibles"""
        return {
            'categories': list(self.datasets.keys()),
            'metadata': self.metadata,
            'total_datasets': sum(len(category) for category in self.datasets.values())
        }
    
    def get_crops_list(self) -> List[str]:
        """Retorna lista de cultivos disponibles"""
        crops = set()
        
        # De datos nacionales
        if 'national_crops' in self.datasets:
            crops.update(self.datasets['national_crops'].keys())
        
        # De datos municipales (extraer de nombres de archivo)
        if 'municipal' in self.datasets:
            for filename in self.datasets['municipal'].keys():
                if '-' in filename:
                    crop = filename.split('-')[1]
                    crops.add(crop)
        
        return sorted(list(crops))
    
    def get_departments_list(self) -> List[str]:
        """Retorna lista de departamentos disponibles"""
        departments = set()
        
        # De datos departamentales
        if 'departmental' in self.datasets:
            departments.update(self.datasets['departmental'].keys())
        
        # De datos nacionales
        if 'national_crops' in self.datasets:
            for df in self.datasets['national_crops'].values():
                if 'Departamento' in df.columns:
                    departments.update(df['Departamento'].unique())
        
        return sorted(list(departments))
    
    def get_years_range(self) -> Dict[str, int]:
        """Retorna rango de años disponibles"""
        years = set()
        
        for category in self.datasets.values():
            for df in category.values():
                if 'Año' in df.columns:
                    years.update(df['Año'].unique())
        
        return {
            'min_year': min(years) if years else 2007,
            'max_year': max(years) if years else 2023,
            'available_years': sorted(list(years))
        }
    
    def filter_data(self, category: str, filters: Dict[str, Any]) -> pd.DataFrame:
        """Filtra datos según criterios especificados"""
        if category not in self.datasets:
            return pd.DataFrame()
        
        # Si se especifica un dataset específico
        if 'dataset' in filters and filters['dataset'] in self.datasets[category]:
            df = self.datasets[category][filters['dataset']].copy()
        else:
            # Combinar todos los datasets de la categoría
            dfs = []
            for dataset_name, dataset_df in self.datasets[category].items():
                dataset_df_copy = dataset_df.copy()
                dataset_df_copy['dataset_source'] = dataset_name
                dfs.append(dataset_df_copy)
            
            if not dfs:
                return pd.DataFrame()
            
            df = pd.concat(dfs, ignore_index=True)
        
        # Aplicar filtros
        if 'year' in filters and 'Año' in df.columns:
            if isinstance(filters['year'], list):
                df = df[df['Año'].isin(filters['year'])]
            else:
                df = df[df['Año'] == filters['year']]
        
        if 'department' in filters and 'Departamento' in df.columns:
            df = df[df['Departamento'].str.contains(filters['department'], case=False, na=False)]
        
        if 'crop' in filters and 'Producto' in df.columns:
            df = df[df['Producto'].str.contains(filters['crop'], case=False, na=False)]
        
        if 'municipality' in filters and 'Municipio' in df.columns:
            df = df[df['Municipio'].str.contains(filters['municipality'], case=False, na=False)]
        
        return df
    
    def get_summary_stats(self, category: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Genera estadísticas resumidas"""
        df = self.filter_data(category, filters or {})
        
        if df.empty:
            return {}
        
        stats = {
            'total_records': len(df),
            'years_covered': [],
            'departments_count': 0,
            'crops_count': 0
        }
        
        if 'Año' in df.columns:
            stats['years_covered'] = sorted(df['Año'].unique().tolist())
        
        if 'Departamento' in df.columns:
            stats['departments_count'] = df['Departamento'].nunique()
        
        if 'Producto' in df.columns:
            stats['crops_count'] = df['Producto'].nunique()
        
        # Estadísticas numéricas
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_columns:
            if col != 'Año':
                stats[f'{col}_total'] = df[col].sum()
                stats[f'{col}_avg'] = df[col].mean()
                stats[f'{col}_max'] = df[col].max()
        
        return stats
    
    def get_chart_data(self, category: str, chart_type: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Genera datos para gráficos"""
        df = self.filter_data(category, filters or {})
        
        if df.empty:
            return {'labels': [], 'datasets': []}
        
        chart_data = {'labels': [], 'datasets': []}
        
        if chart_type == 'production_by_year':
            if 'Año' in df.columns and 'Produccion (ton)' in df.columns:
                yearly_data = df.groupby('Año')['Produccion (ton)'].sum().reset_index()
                chart_data['labels'] = yearly_data['Año'].tolist()
                chart_data['datasets'] = [{
                    'label': 'Producción (ton)',
                    'data': yearly_data['Produccion (ton)'].tolist(),
                    'backgroundColor': 'rgba(74, 124, 89, 0.8)',
                    'borderColor': 'rgba(74, 124, 89, 1)'
                }]
        
        elif chart_type == 'area_by_department':
            if 'Departamento' in df.columns and 'Area (ha)' in df.columns:
                dept_data = df.groupby('Departamento')['Area (ha)'].sum().reset_index()
                dept_data = dept_data.sort_values('Area (ha)', ascending=False).head(10)
                chart_data['labels'] = dept_data['Departamento'].tolist()
                chart_data['datasets'] = [{
                    'label': 'Área (ha)',
                    'data': dept_data['Area (ha)'].tolist(),
                    'backgroundColor': 'rgba(168, 213, 186, 0.8)',
                    'borderColor': 'rgba(168, 213, 186, 1)'
                }]
        
        elif chart_type == 'top_crops':
            if 'Producto' in df.columns and 'Produccion (ton)' in df.columns:
                crop_data = df.groupby('Producto')['Produccion (ton)'].sum().reset_index()
                crop_data = crop_data.sort_values('Produccion (ton)', ascending=False).head(10)
                chart_data['labels'] = crop_data['Producto'].tolist()
                chart_data['datasets'] = [{
                    'label': 'Producción (ton)',
                    'data': crop_data['Produccion (ton)'].tolist(),
                    'backgroundColor': 'rgba(244, 162, 97, 0.8)',
                    'borderColor': 'rgba(244, 162, 97, 1)'
                }]
        
        elif chart_type == 'yield_comparison':
            if 'Departamento' in df.columns and 'Rendimiento (ha/ton)' in df.columns:
                yield_data = df.groupby('Departamento')['Rendimiento (ha/ton)'].mean().reset_index()
                yield_data = yield_data.sort_values('Rendimiento (ha/ton)', ascending=False).head(10)
                chart_data['labels'] = yield_data['Departamento'].tolist()
                chart_data['datasets'] = [{
                    'label': 'Rendimiento Promedio (ha/ton)',
                    'data': yield_data['Rendimiento (ha/ton)'].tolist(),
                    'backgroundColor': 'rgba(107, 155, 122, 0.8)',
                    'borderColor': 'rgba(107, 155, 122, 1)'
                }]
        
        return chart_data

# Instancia global del procesador
data_processor = DataProcessor()
