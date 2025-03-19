"""
Procesador de leads para DB-GPT OVB
Este script procesa archivos CSV y XLSX de leads y los convierte al formato requerido.
"""

import pandas as pd
import json
import random
from datetime import datetime, timedelta
import os
import re
import glob

# Configuración
DIRECTORIO_BASE = os.path.dirname(os.path.abspath(__file__))
DIRECTORIO_ORIGEN = "@9600"
ARCHIVO_DESTINO = "clientes_actuales.py"

def obtener_archivos_csv():
    """Obtiene todos los archivos CSV del directorio @9600"""
    # Primero intentar con el directorio con @
    ruta_con_arroba = os.path.join(DIRECTORIO_BASE, DIRECTORIO_ORIGEN)
    # Si no existe, intentar sin @
    ruta_sin_arroba = os.path.join(DIRECTORIO_BASE, DIRECTORIO_ORIGEN.replace('@', ''))
    
    # Verificar cuál ruta existe
    if os.path.exists(ruta_sin_arroba):
        print(f"Buscando archivos CSV en: {ruta_sin_arroba}")
        return glob.glob(os.path.join(ruta_sin_arroba, '*.csv'))
    else:
        print(f"¡Error! No se encuentra el directorio {DIRECTORIO_ORIGEN}")
        return []

def limpiar_nombre_archivo(nombre):
    """Elimina emojis y caracteres especiales del nombre del archivo"""
    # Eliminar emojis y otros caracteres especiales
    nombre_limpio = re.sub(r'[^\x00-\x7F]+', '', nombre)
    # Eliminar caracteres no permitidos en nombres de archivo
    nombre_limpio = re.sub(r'[<>:"/\\|?*]', '', nombre_limpio)
    # Reemplazar espacios con guiones bajos
    nombre_limpio = nombre_limpio.replace(' ', '_')
    return nombre_limpio

def renombrar_archivo_si_existe(ruta_archivo):
    """Renombra el archivo eliminando emojis si existe"""
    if os.path.exists(ruta_archivo):
        directorio = os.path.dirname(ruta_archivo)
        nombre_archivo = os.path.basename(ruta_archivo)
        nombre_limpio = limpiar_nombre_archivo(nombre_archivo)
        nueva_ruta = os.path.join(directorio, nombre_limpio)
        
        if ruta_archivo != nueva_ruta and not os.path.exists(nueva_ruta):
            try:
                os.rename(ruta_archivo, nueva_ruta)
                print(f"Archivo renombrado: {nombre_archivo} -> {nombre_limpio}")
                return nueva_ruta
            except Exception as e:
                print(f"Error al renombrar archivo: {str(e)}")
                return ruta_archivo
    return ruta_archivo

def procesar_archivo_csv():
    """Procesa el archivo CSV de leads"""
    try:
        # Obtener todos los archivos CSV del directorio
        archivos_csv = obtener_archivos_csv()
        if not archivos_csv:
            print(f"No se encontraron archivos CSV en {DIRECTORIO_ORIGEN}")
            return False

        # Procesar cada archivo encontrado
        todos_los_clientes = []
        for archivo in archivos_csv:
            print(f"Procesando archivo: {archivo}")
            
            # Renombrar el archivo si tiene emojis
            ruta_archivo = renombrar_archivo_si_existe(archivo)
            
            # Intentar diferentes codificaciones
            encodings = ['utf-8', 'latin1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(ruta_archivo, encoding=encoding)
                    print(f"Archivo cargado correctamente con separador ',' y codificación {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                print(f"¡Error! No se pudo leer el archivo {ruta_archivo} con ninguna codificación")
                continue
            
            print(f"Se cargaron {len(df)} registros del archivo CSV")
            
            # Procesar cada registro
            for idx, row in df.iterrows():
                print(f"Procesando registro {idx + 1} de {len(df)}...")
                cliente = procesar_cliente(row, idx)
                todos_los_clientes.append(cliente)
                
                # Mostrar progreso cada 500 registros
                if (idx + 1) % 500 == 0:
                    print(f"Procesando registro {idx + 1} de {len(df)}...")
        
        if todos_los_clientes:
            # Generar archivo Python con la lista de clientes
            print(f"Generando archivo {ARCHIVO_DESTINO} con {len(todos_los_clientes)} clientes...")
            generar_archivo_python(todos_los_clientes)
            print(f"Archivo {ARCHIVO_DESTINO} generado correctamente con {len(todos_los_clientes)} clientes.")
            return True
        else:
            print("No se encontraron clientes para procesar")
            return False
            
    except Exception as e:
        print(f"¡Error! {str(e)}")
        return False

def procesar_cliente(row, idx):
    """Procesa un registro del CSV y lo convierte al formato requerido"""
    
    # Extraer campos básicos
    nombre = f"{str(row.get('Nombre', '')).strip()} {str(row.get('Apellidos', '')).strip()}".strip()
    telefono = str(row.get('Numero de Telefono', '')).strip() if pd.notna(row.get('Numero de Telefono')) else ""
    correo = str(row.get('Correo', '')).strip() if pd.notna(row.get('Correo')) else ""
    ubicacion = str(row.get('Contact Location', '')).strip() if pd.notna(row.get('Contact Location')) else ""
    
    # Determinar método de contacto
    metodo_contacto = "teléfono"
    if correo:
        metodo_contacto = "email"
    elif "www" in str(row.get('Keywords', '')).lower() or "web" in str(row.get('Keywords', '')).lower():
        metodo_contacto = "buscar_en_web"
    elif telefono:
        metodo_contacto = "whatsapp" if random.random() < 0.3 else "teléfono"
    
    # Generar intereses basados en Industry y Keywords
    intereses = generar_intereses(row.get('Industry', ''), row.get('Keywords', ''))
    
    # Calcular puntuación basada en varios factores
    puntuacion = calcular_puntuacion(row)
    
    # Generar datos de geolocalización si hay ubicación
    lat, lon = generar_coordenadas(ubicacion) if ubicacion else ("", "")
    
    # Crear cliente
    cliente = {
        "id": f"ID_{idx}",
        "nombre": nombre,
        "telefono": telefono,
        "correo": correo,
        "metodo_contacto": metodo_contacto,
        "ubicacion": ubicacion,
        "ocupacion": str(row.get('Industry', '')).strip(),
        "intereses": intereses,
        "latitud": lat,
        "longitud": lon,
        "horario": generar_horario(),
        "rating": str(row.get('Employees', '0')),
        "num_reviews": str(random.randint(0, 50)),
        "puntuacion": puntuacion,
        "potencial_inversion": calcular_potencial_inversion(puntuacion),
        "riesgo_crediticio": calcular_riesgo_crediticio(puntuacion),
        "consentimiento_marketing": True,
        "ultima_interaccion": (datetime.now() + timedelta(days=random.randint(0, 730))).strftime("%Y-%m-%d"),
        "historial_compras": []
    }
    
    return cliente

def generar_intereses(industria, keywords):
    """Genera lista de intereses basados en la industria y palabras clave"""
    intereses_base = [
        "planificación jubilación",
        "seguro de vida",
        "inversiones",
        "ahorro",
        "protección familiar",
        "seguro médico",
        "seguro de hogar",
        "plan de pensiones",
        "seguro de negocio",
        "gestión patrimonial"
    ]
    
    intereses_especificos = []
    
    # Añadir intereses basados en la industria
    if isinstance(industria, str):
        if "Management" in industria:
            intereses_especificos.extend(["gestión empresarial", "consultoría financiera"])
        if "Financial" in industria:
            intereses_especificos.extend(["inversiones seguras", "mercados financieros"])
        if "Real Estate" in industria:
            intereses_especificos.extend(["inversión inmobiliaria", "seguros de propiedad"])
        if "Technology" in industria:
            intereses_especificos.extend(["seguro tecnológico", "ciberseguridad"])
        if "Health" in industria:
            intereses_especificos.extend(["seguro de salud", "protección médica"])
    
    # Añadir intereses basados en keywords
    if isinstance(keywords, str):
        if "investment" in keywords.lower():
            intereses_especificos.append("inversiones diversificadas")
        if "consulting" in keywords.lower():
            intereses_especificos.append("asesoramiento financiero")
        if "training" in keywords.lower():
            intereses_especificos.append("educación financiera")
    
    # Combinar y seleccionar aleatoriamente
    todos_intereses = intereses_base + intereses_especificos
    num_intereses = random.randint(3, 5)
    return random.sample(todos_intereses, min(num_intereses, len(todos_intereses)))

def calcular_puntuacion(row):
    """Calcula la puntuación del cliente basada en varios factores"""
    puntuacion = 0
    
    # Puntos por tamaño de empresa
    try:
        empleados = int(row.get('Employees', 0))
        puntuacion += min(empleados * 10, 50)
    except:
        pass
    
    # Puntos por información de contacto
    if pd.notna(row.get('Correo')):
        puntuacion += 20
    if pd.notna(row.get('Numero de Telefono')):
        puntuacion += 15
    if pd.notna(row.get('City')):
        puntuacion += 10
    
    # Puntos por industria
    industrias_premium = ['Financial Services', 'Management Consulting', 'Investment Management']
    if any(ind in str(row.get('Industry', '')) for ind in industrias_premium):
        puntuacion += 25
    
    return min(puntuacion, 100)

def calcular_potencial_inversion(puntuacion):
    """Determina el potencial de inversión basado en la puntuación"""
    if puntuacion >= 75:
        return "alto"
    elif puntuacion >= 50:
        return "medio"
    else:
        return "bajo"

def calcular_riesgo_crediticio(puntuacion):
    """Determina el riesgo crediticio basado en la puntuación"""
    if puntuacion >= 75:
        return "bajo"
    elif puntuacion >= 50:
        return "medio"
    else:
        return "alto"

def generar_coordenadas(ubicacion):
    """Genera coordenadas aleatorias para una ubicación en España"""
    # Coordenadas aproximadas de España
    lat = random.uniform(36.0, 43.8)
    lon = random.uniform(-9.3, 3.3)
    return f"{lat:.6f}", f"{lon:.6f}"

def generar_horario():
    """Genera un horario comercial aleatorio"""
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    horario = {}
    
    for dia in dias:
        if dia in ["sábado", "domingo"]:
            horario[dia] = ""  # Cerrado fines de semana
        else:
            # 70% de probabilidad de tener horario comercial
            if random.random() < 0.7:
                horario[dia] = "09:00-18:00"
            else:
                horario[dia] = ""
    
    return horario

def generar_archivo_python(clientes):
    """Genera un archivo Python con la lista de clientes"""
    with open('clientes_actuales.py', 'w', encoding='utf-8') as f:
        f.write('# -*- coding: utf-8 -*-\n\n')
        f.write('"""Base de datos de clientes para OVB"""\n\n')
        f.write('clientes = [\n')
        
        for cliente in clientes:
            # Convertir el diccionario a string, asegurando que los booleanos sean True/False
            cliente_str = str(cliente).replace('true', 'True').replace('false', 'False')
            f.write(f'    {cliente_str},\n')
        
        f.write(']\n\n')
        f.write('def obtener_clientes():\n')
        f.write('    return clientes\n\n')
        f.write('def obtener_cliente_por_id(id):\n')
        f.write('    return next((c for c in clientes if c["id"] == id), None)\n\n')
        f.write('def filtrar_clientes_por_criterio(criterio, valor):\n')
        f.write('    return [c for c in clientes if str(c.get(criterio, "")).lower() == str(valor).lower()]')

if __name__ == "__main__":
    procesar_archivo_csv() 