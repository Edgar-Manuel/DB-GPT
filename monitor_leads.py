"""
Monitor automático de nuevos leads para DB-GPT OVB

Este script monitorea la carpeta de leads en busca de nuevos archivos CSV y XLSX
y los procesa automáticamente, actualizando la base de datos de clientes.
"""

import os
import time
import json
import logging
import pandas as pd
import sys
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import procesar_leads

# Configuración para manejar caracteres especiales en Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Configuración de directorios
CARPETA_LEADS = "9600"
CARPETA_RESULTADOS = "resultados_monitor"
CARPETA_LOGS = os.path.join(CARPETA_RESULTADOS, "logs")
CARPETA_PROCESADOS = os.path.join(CARPETA_RESULTADOS, "procesados")

# Crear estructura de directorios
os.makedirs(CARPETA_LEADS, exist_ok=True)
os.makedirs(CARPETA_LOGS, exist_ok=True)
os.makedirs(CARPETA_PROCESADOS, exist_ok=True)

# Configuración de logging con codificación UTF-8
class UTF8StreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            stream.buffer.write(msg.encode('utf-8'))
            stream.buffer.write(self.terminator.encode('utf-8'))
            self.flush()
        except Exception:
            self.handleError(record)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(CARPETA_LOGS, 'monitor_leads.log'), encoding='utf-8'),
        UTF8StreamHandler()
    ]
)

# Configuración
ARCHIVO_REGISTRO = os.path.join(CARPETA_RESULTADOS, "leads_procesados.json")
INTERVALO_ESCANEO = 86400  # 24 horas en segundos
EXTENSIONES_VALIDAS = {'.csv', '.xlsx', '.xls'}

class ProcesadorLeads:
    def __init__(self):
        self.leads_procesados = self.cargar_registro()
        
    def cargar_registro(self):
        """Carga el registro de archivos procesados"""
        if os.path.exists(ARCHIVO_REGISTRO):
            try:
                with open(ARCHIVO_REGISTRO, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def guardar_registro(self):
        """Guarda el registro de archivos procesados"""
        with open(ARCHIVO_REGISTRO, 'w', encoding='utf-8') as f:
            json.dump(self.leads_procesados, f, indent=4, ensure_ascii=False)
    
    def convertir_excel_a_csv(self, ruta_excel):
        """Convierte un archivo Excel a CSV"""
        try:
            # Leer el archivo Excel
            df = pd.read_excel(ruta_excel)
            
            # Generar nombre para el archivo CSV en la carpeta de procesados
            nombre_base = os.path.splitext(os.path.basename(ruta_excel))[0]
            ruta_csv = os.path.join(CARPETA_PROCESADOS, f"{nombre_base}_convertido.csv")
            
            # Guardar como CSV
            df.to_csv(ruta_csv, index=False, encoding='utf-8')
            logging.info(f"Archivo Excel convertido exitosamente a CSV: {ruta_csv}")
            
            # Crear un resumen del procesamiento
            resumen = {
                "total_registros": len(df),
                "columnas": list(df.columns),
                "fecha_conversion": datetime.now().isoformat()
            }
            
            # Guardar resumen
            ruta_resumen = os.path.join(CARPETA_PROCESADOS, f"{nombre_base}_resumen.json")
            with open(ruta_resumen, 'w', encoding='utf-8') as f:
                json.dump(resumen, f, indent=4, ensure_ascii=False)
            
            return ruta_csv
        except Exception as e:
            logging.error(f"Error al convertir Excel a CSV: {str(e)}")
            return None
    
    def procesar_archivo(self, ruta_archivo):
        """Procesa un nuevo archivo de leads"""
        nombre_archivo = os.path.basename(ruta_archivo)
        extension = os.path.splitext(ruta_archivo)[1].lower()
        
        # Verificar si ya fue procesado
        if nombre_archivo in self.leads_procesados:
            logging.info(f"El archivo {nombre_archivo} ya fue procesado anteriormente")
            return False
        
        try:
            ruta_a_procesar = ruta_archivo
            
            # Si es Excel, convertir a CSV primero
            if extension in {'.xlsx', '.xls'}:
                ruta_a_procesar = self.convertir_excel_a_csv(ruta_archivo)
                if not ruta_a_procesar:
                    return False
            
            # Modificar temporalmente la ruta en procesar_leads.py
            ruta_original = procesar_leads.ARCHIVO_ORIGEN
            procesar_leads.ARCHIVO_ORIGEN = ruta_a_procesar
            
            # Procesar el archivo
            logging.info(f"Procesando nuevo archivo: {nombre_archivo}")
            if procesar_leads.procesar_archivo_csv():
                # Registrar el procesamiento exitoso
                self.leads_procesados[nombre_archivo] = {
                    "fecha_procesado": datetime.now().isoformat(),
                    "ruta_original": ruta_archivo,
                    "ruta_procesada": ruta_a_procesar if extension != '.csv' else ruta_archivo,
                    "total_procesados": procesar_leads.total_procesados if hasattr(procesar_leads, 'total_procesados') else 0
                }
                self.guardar_registro()
                logging.info(f"Archivo {nombre_archivo} procesado exitosamente")
                return True
            
        except Exception as e:
            logging.error(f"Error al procesar {nombre_archivo}: {str(e)}")
            
        finally:
            # Restaurar la ruta original
            procesar_leads.ARCHIVO_ORIGEN = ruta_original
        
        return False

class MonitorLeads(FileSystemEventHandler):
    def __init__(self):
        self.procesador = ProcesadorLeads()
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        extension = os.path.splitext(event.src_path)[1].lower()
        if extension in EXTENSIONES_VALIDAS:
            logging.info(f"Nuevo archivo detectado: {event.src_path}")
            self.procesador.procesar_archivo(event.src_path)
    
    def escanear_archivos_existentes(self):
        """Escanea y procesa archivos existentes"""
        carpeta = Path(CARPETA_LEADS)
        if not carpeta.exists():
            logging.error(f"La carpeta {CARPETA_LEADS} no existe")
            return
        
        for extension in EXTENSIONES_VALIDAS:
            for archivo in carpeta.glob(f"*{extension}"):
                self.procesador.procesar_archivo(str(archivo))

def iniciar_monitor():
    """Inicia el monitor de archivos"""
    logging.info("Iniciando monitor de leads...")
    logging.info(f"Resultados se guardarán en: {os.path.abspath(CARPETA_RESULTADOS)}")
    
    # Configurar el observer
    monitor = MonitorLeads()
    observer = Observer()
    observer.schedule(monitor, CARPETA_LEADS, recursive=False)
    observer.start()
    
    try:
        # Escanear archivos existentes primero
        monitor.escanear_archivos_existentes()
        
        while True:
            # Escanear periódicamente
            time.sleep(INTERVALO_ESCANEO)
            logging.info("Realizando escaneo programado...")
            monitor.escanear_archivos_existentes()
            
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Monitor detenido por el usuario")
    
    observer.join()

if __name__ == "__main__":
    iniciar_monitor() 