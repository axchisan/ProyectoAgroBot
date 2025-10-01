from flask import Blueprint, render_template, request, jsonify # type: ignore
from ..data_processor import data_processor
import json
import pandas as pd # type: ignore
import numpy as np # type: ignore

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
def dashboard():
    """Dashboard principal de analytics"""
    # Obtener información general de los datasets
    datasets_info = data_processor.get_available_datasets()
    crops_list = data_processor.get_crops_list()
    departments_list = data_processor.get_departments_list()
    years_range = data_processor.get_years_range()
    
    # Estadísticas generales
    general_stats = {}
    for category in datasets_info['categories']:
        general_stats[category] = data_processor.get_summary_stats(category)
    
    print(datasets_info.metadata)
    return render_template('analytics/dashboard.html',
                         datasets_info=datasets_info,
                         crops_list=crops_list[:20],  # Mostrar solo los primeros 20
                         departments_list=departments_list,
                         years_range=years_range,
                         general_stats=general_stats)

@analytics_bp.route('/national-crops')
def national_crops():
    """Vista de datos nacionales por cultivo"""
    crops_list = data_processor.get_crops_list()
    departments_list = data_processor.get_departments_list()
    years_range = data_processor.get_years_range()
    
    # Filtros de la URL
    selected_crop = request.args.get('crop', '')
    selected_department = request.args.get('department', '')
    selected_year = request.args.get('year', '')
    
    # Aplicar filtros
    filters = {}
    if selected_crop:
        filters['crop'] = selected_crop
    if selected_department:
        filters['department'] = selected_department
    if selected_year:
        filters['year'] = int(selected_year)
    
    # Obtener datos filtrados
    filtered_data = data_processor.filter_data('national_crops', filters)
    summary_stats = data_processor.get_summary_stats('national_crops', filters)
    
    # Datos para gráficos
    production_chart = data_processor.get_chart_data('national_crops', 'production_by_year', filters)
    department_chart = data_processor.get_chart_data('national_crops', 'area_by_department', filters)
    
    return render_template('analytics/national_crops.html',
                         crops_list=crops_list,
                         departments_list=departments_list,
                         years_range=years_range,
                         selected_crop=selected_crop,
                         selected_department=selected_department,
                         selected_year=selected_year,
                         filtered_data=filtered_data.head(100).to_dict('records'),
                         summary_stats=summary_stats,
                         production_chart=json.dumps(production_chart),
                         department_chart=json.dumps(department_chart))

@analytics_bp.route('/municipal-data')
def municipal_data():
    """Vista de datos municipales"""
    departments_list = data_processor.get_departments_list()
    years_range = data_processor.get_years_range()
    
    # Obtener datasets municipales disponibles
    municipal_datasets = list(data_processor.datasets.get('municipal', {}).keys())
    
    # Filtros
    selected_dataset = request.args.get('dataset', '')
    selected_year = request.args.get('year', '')
    selected_municipality = request.args.get('municipality', '')
    
    filters = {}
    if selected_dataset:
        filters['dataset'] = selected_dataset
    if selected_year:
        filters['year'] = int(selected_year)
    if selected_municipality:
        filters['municipality'] = selected_municipality
    
    # Obtener datos
    filtered_data = data_processor.filter_data('municipal', filters)
    summary_stats = data_processor.get_summary_stats('municipal', filters)
    
    # Agregar conteo de municipios si es q hay datos
    if not filtered_data.empty and 'Municipio' in filtered_data.columns:
        summary_stats['municipalities_count'] = filtered_data['Municipio'].nunique()
    
    return render_template('analytics/municipal_data.html',
                         departments_list=departments_list,
                         years_range=years_range,
                         municipal_datasets=municipal_datasets,
                         selected_dataset=selected_dataset,
                         selected_year=selected_year,
                         selected_municipality=selected_municipality,
                         filtered_data=filtered_data.head(100).to_dict('records'),
                         summary_stats=summary_stats)

@analytics_bp.route('/departmental-comparison')
def departmental_comparison():
    """Vista de comparación departamental"""
    departments_list = data_processor.get_departments_list()
    crops_list = data_processor.get_crops_list()
    years_range = data_processor.get_years_range()
    
    # Filtros
    selected_departments = request.args.getlist('departments')
    selected_crop = request.args.get('crop', '')
    selected_year = request.args.get('year', '')
    
    filters = {}
    if selected_crop:
        filters['crop'] = selected_crop
    if selected_year:
        filters['year'] = int(selected_year)
    
    
    filtered_data = data_processor.filter_data('departmental', filters)
    
    # Filtrar por departamentos seleccionados
    if selected_departments and 'Departamento' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['Departamento'].isin(selected_departments)]
    
    summary_stats = data_processor.get_summary_stats('departmental', filters)
    
    return render_template('analytics/departmental_comparison.html',
                         departments_list=departments_list,
                         crops_list=crops_list,
                         years_range=years_range,
                         selected_departments=selected_departments,
                         selected_crop=selected_crop,
                         selected_year=selected_year,
                         filtered_data=filtered_data.head(100).to_dict('records'),
                         summary_stats=summary_stats)

@analytics_bp.route('/departmental-participation')
def departmental_participation():
    """Vista de participación departamental"""
    departments_list = data_processor.get_departments_list()
    crops_list = data_processor.get_crops_list()
    years_range = data_processor.get_years_range()
    
    # Filtros
    selected_department = request.args.get('department', '')
    selected_crop = request.args.get('crop', '')
    selected_year = request.args.get('year', '')
    
    filters = {}
    if selected_department:
        filters['department'] = selected_department
    if selected_crop:
        filters['crop'] = selected_crop
    if selected_year:
        filters['year'] = int(selected_year)
    
    # Obtener datos
    filtered_data = data_processor.filter_data('departmental', filters)
    
    # Calcular porcentajes de participación 
    if not filtered_data.empty:
        # Agrupar por año y producto para obtener totales nacionales
        if 'Año' in filtered_data.columns and 'Producto' in filtered_data.columns:
            national_totals = filtered_data.groupby(['Año', 'Producto']).agg({
                'Area (ha)': 'sum',
                'Produccion (ton)': 'sum'
            }).reset_index()
            
            # Renombrar columnas para evitar conflictos
            national_totals = national_totals.rename(columns={
                'Area (ha)': 'Area_Nacional',
                'Produccion (ton)': 'Produccion_Nacional'
            })
            
            # Fusionar con datos originales
            merged_data = pd.merge(
                filtered_data,
                national_totals,
                on=['Año', 'Producto'],
                how='left'
            )
            
            # Calcular porcentajes
            merged_data['Porcentaje_Area'] = (merged_data['Area (ha)'] / merged_data['Area_Nacional']) * 100
            merged_data['Porcentaje_Produccion'] = (merged_data['Produccion (ton)'] / merged_data['Produccion_Nacional']) * 100
            
            # Reemplazar datos filtrados con los datos enriquecidos
            filtered_data = merged_data
    
    summary_stats = data_processor.get_summary_stats('departmental', filters)
    
    return render_template('analytics/departmental_participation.html',
                         departments_list=departments_list,
                         crops_list=crops_list,
                         years_range=years_range,
                         selected_department=selected_department,
                         selected_crop=selected_crop,
                         selected_year=selected_year,
                         filtered_data=filtered_data.head(100).to_dict('records'),
                         summary_stats=summary_stats)

@analytics_bp.route('/api/chart-data')
def api_chart_data():
    """API para obtener datos de gráficos dinámicamente"""
    category = request.args.get('category', 'national_crops')
    chart_type = request.args.get('chart_type', 'production_by_year')
    
    # Construir filtros desde parámetros
    filters = {}
    if request.args.get('crop'):
        filters['crop'] = request.args.get('crop')
    if request.args.get('department'):
        filters['department'] = request.args.get('department')
    if request.args.get('year'):
        filters['year'] = int(request.args.get('year'))
    if request.args.get('dataset'):
        filters['dataset'] = request.args.get('dataset')
    
    # filtros para comparación departamental
    if request.args.get('departments'):
        departments = request.args.get('departments').split(',')
        filters['departments'] = departments
    
    # Tipos de gráficos específicos para datos municipales
    if category == 'municipal' and chart_type == 'top_municipalities':
        chart_data = get_top_municipalities_chart(filters)
    elif category == 'municipal' and chart_type == 'yield_comparison':
        chart_data = get_yield_comparison_chart(filters)
    # Tipos de gráficos específicos para comparación departamental
    elif category == 'departmental' and chart_type in ['production_comparison', 'area_comparison', 'yield_comparison']:
        chart_data = get_departmental_comparison_chart(chart_type, filters)
    # Tipos de gráficos específicos para participación departamental
    elif category == 'departmental' and chart_type == 'production_share':
        chart_data = get_production_share_chart(filters)
    elif category == 'departmental' and chart_type == 'area_share':
        chart_data = get_area_share_chart(filters)
    elif category == 'departmental' and chart_type == 'participation_trends':
        chart_data = get_participation_trends_chart(filters)
    else:
        # Gráficos estándar
        chart_data = data_processor.get_chart_data(category, chart_type, filters)
    
    return jsonify(chart_data)

def get_top_municipalities_chart(filters):
    """Genera datos para gráfico de top municipios por producción"""
    df = data_processor.filter_data('municipal', filters)
    
    if df.empty or 'Municipio' not in df.columns or 'Produccion (ton)' not in df.columns:
        return {'labels': [], 'datasets': []}
    
    # Agrupar por municipio y sumar producción
    muni_data = df.groupby('Municipio')['Produccion (ton)'].sum().reset_index()
    muni_data = muni_data.sort_values('Produccion (ton)', ascending=False).head(10)
    
    return {
        'labels': muni_data['Municipio'].tolist(),
        'datasets': [{
            'label': 'Producción (ton)',
            'data': muni_data['Produccion (ton)'].tolist(),
            'backgroundColor': 'rgba(74, 124, 89, 0.8)',
            'borderColor': 'rgba(74, 124, 89, 1)'
        }]
    }

def get_yield_comparison_chart(filters):
    """Genera datos para gráfico de comparación de rendimiento por municipio"""
    df = data_processor.filter_data('municipal', filters)
    
    if df.empty or 'Municipio' not in df.columns or 'Rendimiento (ha/ton)' not in df.columns:
        return {'labels': [], 'datasets': []}
    
    # Agrupar por municipio y calcular rendimiento promedio
    yield_data = df.groupby('Municipio')['Rendimiento (ha/ton)'].mean().reset_index()
    yield_data = yield_data.sort_values('Rendimiento (ha/ton)', ascending=False).head(10)
    
    return {
        'labels': yield_data['Municipio'].tolist(),
        'datasets': [{
            'label': 'Rendimiento (ha/ton)',
            'data': yield_data['Rendimiento (ha/ton)'].tolist(),
            'backgroundColor': 'rgba(244, 162, 97, 0.8)',
            'borderColor': 'rgba(244, 162, 97, 1)'
        }]
    }

def get_departmental_comparison_chart(chart_type, filters):
    """Genera datos para gráficos de comparación departamental"""
    df = data_processor.filter_data('departmental', filters)
    
    # Filtrar por departamentos seleccionados
    if 'departments' in filters and 'Departamento' in df.columns:
        df = df[df['Departamento'].isin(filters['departments'])]
    
    if df.empty:
        return {'labels': [], 'datasets': []}
    
    # Determinar qué columna usar según el tipo de gráfico
    if chart_type == 'production_comparison':
        value_column = 'Produccion (ton)'
        label = 'Producción (ton)'
    elif chart_type == 'area_comparison':
        value_column = 'Area (ha)'
        label = 'Área (ha)'
    else:  # yield_comparison
        value_column = 'Rendimiento (ha/ton)'
        label = 'Rendimiento (ha/ton)'
    
    if value_column not in df.columns:
        return {'labels': [], 'datasets': []}
    
    # Para gráficos de radar (rendimiento)
    if chart_type == 'yield_comparison':
        # Agrupar por departamento y producto, calcular rendimiento promedio
        if 'Producto' in df.columns:
            pivot_data = df.pivot_table(
                index='Departamento', 
                columns='Producto', 
                values=value_column,
                aggfunc='mean'
            ).fillna(0)
            
            return {
                'labels': pivot_data.columns.tolist(),
                'datasets': [
                    {
                        'label': dept,
                        'data': pivot_data.loc[dept].tolist(),
                        'fill': True,
                        'backgroundColor': f'rgba({74 + i*30}, {124 + i*20}, {89 + i*10}, 0.2)',
                        'borderColor': f'rgba({74 + i*30}, {124 + i*20}, {89 + i*10}, 1)',
                        'pointBackgroundColor': f'rgba({74 + i*30}, {124 + i*20}, {89 + i*10}, 1)',
                    }
                    for i, dept in enumerate(pivot_data.index)
                ]
            }
    
    # ráficos de barras producción y área
    dept_data = df.groupby('Departamento')[value_column].sum().reset_index()
    dept_data = dept_data.sort_values(value_column, ascending=False)
    
    return {
        'labels': dept_data['Departamento'].tolist(),
        'datasets': [{
            'label': label,
            'data': dept_data[value_column].tolist(),
            'backgroundColor': [
                f'rgba({74 + i*30}, {124 + i*20}, {89 + i*10}, 0.8)'
                for i in range(len(dept_data))
            ],
            'borderColor': [
                f'rgba({74 + i*30}, {124 + i*20}, {89 + i*10}, 1)'
                for i in range(len(dept_data))
            ]
        }]
    }

def get_production_share_chart(filters):
    """Genera datos para gráfico de participación en producción"""
    df = data_processor.filter_data('departmental', filters)
    
    if df.empty or 'Departamento' not in df.columns or 'Produccion (ton)' not in df.columns:
        return {'labels': [], 'datasets': []}
    
    # Filtrar por año específico 
    if 'year' in filters and 'Año' in df.columns:
        df = df[df['Año'] == filters['year']]
    
    # Agrupar por departamento y sumar producción
    dept_data = df.groupby('Departamento')['Produccion (ton)'].sum().reset_index()
    
    # Calcular porcentaje de participación
    total_production = dept_data['Produccion (ton)'].sum()
    dept_data['Porcentaje'] = (dept_data['Produccion (ton)'] / total_production) * 100
    
    # Ordenar por porcentaje descendente
    dept_data = dept_data.sort_values('Porcentaje', ascending=False)
    
    # Limitar a los 10 principales departamentos aagrupar el resto como "Otros"
    if len(dept_data) > 10:
        top_depts = dept_data.head(10)
        others = pd.DataFrame({
            'Departamento': ['Otros'],
            'Produccion (ton)': [dept_data.iloc[10:]['Produccion (ton)'].sum()],
            'Porcentaje': [dept_data.iloc[10:]['Porcentaje'].sum()]
        })
        dept_data = pd.concat([top_depts, others])
    
    return {
        'labels': dept_data['Departamento'].tolist(),
        'datasets': [{
            'label': 'Participación en Producción (%)',
            'data': dept_data['Porcentaje'].tolist(),
        }]
    }

def get_area_share_chart(filters):
    """Genera datos para gráfico de participación en área"""
    df = data_processor.filter_data('departmental', filters)
    
    if df.empty or 'Departamento' not in df.columns or 'Area (ha)' not in df.columns:
        return {'labels': [], 'datasets': []}
    
    # Filtrar por año específico si se da
    if 'year' in filters and 'Año' in df.columns:
        df = df[df['Año'] == filters['year']]
    
    # Agrupar por departamento y sumar área
    dept_data = df.groupby('Departamento')['Area (ha)'].sum().reset_index()
    
    # Calculo porcentaje de participación
    total_area = dept_data['Area (ha)'].sum()
    dept_data['Porcentaje'] = (dept_data['Area (ha)'] / total_area) * 100
    
    # Ordenar por porcentaje descendente
    dept_data = dept_data.sort_values('Porcentaje', ascending=False)
    
    # Limitar a los 10 principales departamentos y agrupar el resto como Otros
    if len(dept_data) > 10:
        top_depts = dept_data.head(10)
        others = pd.DataFrame({
            'Departamento': ['Otros'],
            'Area (ha)': [dept_data.iloc[10:]['Area (ha)'].sum()],
            'Porcentaje': [dept_data.iloc[10:]['Porcentaje'].sum()]
        })
        dept_data = pd.concat([top_depts, others])
    
    return {
        'labels': dept_data['Departamento'].tolist(),
        'datasets': [{
            'label': 'Participación en Área (%)',
            'data': dept_data['Porcentaje'].tolist(),
        }]
    }

def get_participation_trends_chart(filters):
    """Genera datos para gráfico de tendencias de participación"""
    df = data_processor.filter_data('departmental', filters)
    
    if df.empty or 'Departamento' not in df.columns or 'Año' not in df.columns:
        return {'labels': [], 'datasets': []}
    
    # Filtrar por departamento específico si se proporciona
    selected_dept = None
    if 'department' in filters:
        selected_dept = filters['department']
        df = df[df['Departamento'] == selected_dept]
    
    # Filtrar por cultivo específico si se proporciona
    if 'crop' in filters and 'Producto' in df.columns:
        df = df[df['Producto'] == filters['crop']]
    
    # Si no hay datos después de filtrar, retornar vacío
    if df.empty:
        return {'labels': [], 'datasets': []}
    
    # Agrupar por año y departamento
    years = sorted(df['Año'].unique())
    
    # Si no se seleccionó un departamento específico, tomar los 5 principales
    if not selected_dept:
        # Determinar los 5 principales departamentos por producción total
        top_depts = df.groupby('Departamento')['Produccion (ton)'].sum().nlargest(5).index.tolist()
        df = df[df['Departamento'].isin(top_depts)]
    
    # Calcular participación por año para cada departamento
    result = {'labels': years, 'datasets': []}
    
    # Calcular totales nacionales por año
    yearly_totals = df.groupby('Año').agg({
        'Produccion (ton)': 'sum',
        'Area (ha)': 'sum'
    })
    
    # Para cada departamento, calcular su participación anual
    for dept in df['Departamento'].unique():
        dept_data = df[df['Departamento'] == dept]
        dept_yearly = dept_data.groupby('Año').agg({
            'Produccion (ton)': 'sum',
            'Area (ha)': 'sum'
        })
        
        # Calcular porcentajes de participación
        participation = []
        for year in years:
            if year in dept_yearly.index and year in yearly_totals.index:
                if yearly_totals.loc[year, 'Produccion (ton)'] > 0:
                    part = (dept_yearly.loc[year, 'Produccion (ton)'] / yearly_totals.loc[year, 'Produccion (ton)']) * 100
                    participation.append(part)
                else:
                    participation.append(0)
            else:
                participation.append(0)
        
        # Generar color aleatorio pero consistente para el departamento
        color_seed = sum(ord(c) for c in dept)
        r = (color_seed * 123) % 200 + 55
        g = (color_seed * 45) % 200 + 55
        b = (color_seed * 67) % 200 + 55
        
        result['datasets'].append({
            'label': dept,
            'data': participation,
            'borderColor': f'rgba({r}, {g}, {b}, 1)',
            'backgroundColor': f'rgba({r}, {g}, {b}, 0.2)',
            'fill': False,
            'tension': 0.1
        })
    
    return result

@analytics_bp.route('/api/summary-stats')
def api_summary_stats():
    """API para obtener estadísticas resumidas"""
    category = request.args.get('category', 'national_crops')
    
    filters = {}
    if request.args.get('crop'):
        filters['crop'] = request.args.get('crop')
    if request.args.get('department'):
        filters['department'] = request.args.get('department')
    if request.args.get('year'):
        filters['year'] = int(request.args.get('year'))
    
    stats = data_processor.get_summary_stats(category, filters)
    return jsonify(stats)

@analytics_bp.route('/export')
def export_data():
    """Exportar datos filtrados"""
    category = request.args.get('category', 'national_crops')
    format_type = request.args.get('format', 'csv')
    
    #filtros
    filters = {}
    for param in ['crop', 'department', 'year', 'dataset', 'municipality']:
        if request.args.get(param):
            if param == 'year':
                filters[param] = int(request.args.get(param))
            else:
                filters[param] = request.args.get(param)
    
    # Manejar departamentos múltiples
    if request.args.getlist('departments'):
        filters['departments'] = request.args.getlist('departments')
    
    # Obtener datos filtrados
    filtered_data = data_processor.filter_data(category, filters)
    
    # Filtrar por departamentos si es comparación departamental
    if 'departments' in filters and 'Departamento' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['Departamento'].isin(filters['departments'])]
    
    # Para participación departamental, calcular porcentajes
    if category == 'departmental' and 'Departamento' in filtered_data.columns:
        # Agrupar por año y producto para obtener totales nacionales
        if 'Año' in filtered_data.columns and 'Producto' in filtered_data.columns:
            national_totals = filtered_data.groupby(['Año', 'Producto']).agg({
                'Area (ha)': 'sum',
                'Produccion (ton)': 'sum'
            }).reset_index()
            
            # Renombrar columnas para evitar conflictos
            national_totals = national_totals.rename(columns={
                'Area (ha)': 'Area_Nacional',
                'Produccion (ton)': 'Produccion_Nacional'
            })
            
            # Fusionar con datos originales
            merged_data = pd.merge(
                filtered_data,
                national_totals,
                on=['Año', 'Producto'],
                how='left'
            )
            
            # Calcular porcentajes
            merged_data['Porcentaje_Area'] = (merged_data['Area (ha)'] / merged_data['Area_Nacional']) * 100
            merged_data['Porcentaje_Produccion'] = (merged_data['Produccion (ton)'] / merged_data['Produccion_Nacional']) * 100
            
            # Reemplazar datos filtrados con los datos enriquecidos
            filtered_data = merged_data
    
    if format_type == 'json':
        return jsonify(filtered_data.to_dict('records'))
    else:
        # CSV por defecto
        from flask import Response # type: ignore
        csv_data = filtered_data.to_csv(index=False)
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={category}_data.csv'}
        )
