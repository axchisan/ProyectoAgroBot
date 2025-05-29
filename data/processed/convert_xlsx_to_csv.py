import os
import pandas as pd # type: ignore

# Directorios de entrada y salida
input_folder = "./"  # Cambia esto a la ruta de tu carpeta con archivos XLSX
output_folder = "./"  # Cambia esto a la ruta donde quieres guardar los CSVs

# Crear la carpeta de salida si no existe
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Recorrer todos los archivos en la carpeta de entrada
for filename in os.listdir(input_folder):
    if filename.endswith(".xlsx"):
        # Ruta completa del archivo XLSX
        xlsx_path = os.path.join(input_folder, filename)
        
        # Leer el archivo XLSX
        try:
            df = pd.read_excel(xlsx_path)
            
            # Generar el nombre del archivo CSV (mismo nombre, pero con extensión .csv)
            csv_filename = os.path.splitext(filename)[0] + ".csv"
            csv_path = os.path.join(output_folder, csv_filename)
            
            # Guardar como CSV
            df.to_csv(csv_path, index=False, encoding='utf-8')
            print(f"Convertido: {filename} -> {csv_filename}")
        except Exception as e:
            print(f"Error al procesar {filename}: {e}")

print("Conversión completada.")