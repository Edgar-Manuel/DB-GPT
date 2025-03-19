from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
import json
import sys
import os
import math
import subprocess
import threading
import importlib
import traceback
import time

# Añadir el directorio padre al path para poder importar clientes_actuales
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Variables globales para logs y procesos
procesos_activos = {}
logs_procesos = {}
MAX_LOG_ENTRIES = 1000

# Cargar clientes una vez al inicio y almacenarlos en una variable global
try:
    import clientes_actuales
    CLIENTES_GLOBALES = clientes_actuales.clientes
    print(f"Cargados inicialmente {len(CLIENTES_GLOBALES)} clientes")
except Exception as e:
    print(f"Error al cargar clientes inicialmente: {str(e)}")
    CLIENTES_GLOBALES = []

app = Flask(__name__)
app.secret_key = "ovb_dashboard_secret_key"  # Necesario para usar flash messages

def cargar_clientes(forzar_recarga=False):
    """Recarga el módulo clientes_actuales y devuelve la lista actualizada de clientes"""
    global CLIENTES_GLOBALES
    
    if not forzar_recarga and CLIENTES_GLOBALES:
        return CLIENTES_GLOBALES
        
    try:
        # Eliminar del cache si ya existe
        if 'clientes_actuales' in sys.modules:
            del sys.modules['clientes_actuales']
        
        # Importar el módulo de nuevo
        import clientes_actuales
        
        # Verificar datos
        clientes = clientes_actuales.clientes
        num_clientes = len(clientes)
        print(f"Cargando datos: {num_clientes} clientes encontrados")
        
        # Actualizar variable global
        CLIENTES_GLOBALES = clientes
        
        return clientes
    except Exception as e:
        print(f"Error al cargar clientes: {str(e)}")
        traceback.print_exc()
        return CLIENTES_GLOBALES if CLIENTES_GLOBALES else []

@app.route('/')
def index():
    # Recargar clientes si es necesario
    clientes = cargar_clientes(forzar_recarga=request.args.get('recargar', False))
    
    # Estadísticas generales
    total_clientes = len(clientes)
    clientes_alta_puntuacion = len([c for c in clientes if c['puntuacion'] >= 35])
    productos_populares = {}
    
    if total_clientes > 0:
        for cliente in clientes:
            for interes in cliente.get('intereses', []):
                productos_populares[interes] = productos_populares.get(interes, 0) + 1
        
        top_productos = sorted(productos_populares.items(), key=lambda x: x[1], reverse=True)[:5]
        porcentaje_premium = round((clientes_alta_puntuacion/total_clientes)*100, 1)
    else:
        top_productos = []
        porcentaje_premium = 0
    
    stats = {
        'total_clientes': total_clientes,
        'clientes_premium': clientes_alta_puntuacion,
        'porcentaje_premium': porcentaje_premium,
        'top_productos': top_productos
    }
    
    # Top 10 clientes
    top_clientes = sorted(clientes, key=lambda x: (x['puntuacion'], len(x.get('intereses', []))), reverse=True)[:10]
    
    return render_template('index.html', stats=stats, top_clientes=top_clientes)

@app.route('/recargar-datos')
def recargar_datos():
    """Ruta para forzar la recarga de datos"""
    try:
        clientes = cargar_clientes(forzar_recarga=True)
        flash(f"Datos recargados correctamente. {len(clientes)} clientes encontrados.", "success")
    except Exception as e:
        flash(f"Error al recargar datos: {str(e)}", "danger")
    
    return redirect(url_for('index'))

@app.route('/todos-clientes')
def todos_clientes():
    # Recargar clientes si es necesario
    clientes = cargar_clientes(forzar_recarga=request.args.get('recargar', False))
    
    # Obtener parámetros de paginación
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Calcular total de páginas
    total_clientes = len(clientes)
    total_pages = math.ceil(total_clientes / per_page)
    
    # Calcular índices de inicio y fin para la página actual
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_clientes)
    
    # Ordenar clientes por puntuación y obtener los de la página actual
    sorted_clientes = sorted(clientes, key=lambda x: (x['puntuacion'], len(x.get('intereses', []))), reverse=True)
    current_page_clientes = sorted_clientes[start_idx:end_idx]
    
    # Generar recomendaciones principales para cada cliente
    for cliente in current_page_clientes:
        if cliente['puntuacion'] >= 35:
            cliente['recomendacion_principal'] = 'Plan Inversión Premium'
        elif cliente['puntuacion'] >= 20:
            cliente['recomendacion_principal'] = 'Plan Protección Integral Plus'
        else:
            cliente['recomendacion_principal'] = 'Plan Inicial Flexible'
    
    return render_template('todos_clientes.html', 
                          clientes=current_page_clientes, 
                          page=page, 
                          per_page=per_page,
                          total_pages=total_pages,
                          total_clientes=total_clientes)

@app.route('/api/clientes')
def get_clientes():
    # Recargar clientes si es necesario
    clientes = cargar_clientes(forzar_recarga=request.args.get('recargar', False))
    return jsonify(clientes)

@app.route('/api/stats')
def get_stats():
    # Recargar clientes si es necesario
    clientes = cargar_clientes(forzar_recarga=request.args.get('recargar', False))
    
    # Estadísticas para gráficos
    puntuaciones = {}
    intereses = {}
    metodos_contacto = {}
    
    for cliente in clientes:
        # Contar puntuaciones
        punt = cliente['puntuacion']
        puntuaciones[punt] = puntuaciones.get(punt, 0) + 1
        
        # Contar intereses
        for interes in cliente.get('intereses', []):
            intereses[interes] = intereses.get(interes, 0) + 1
            
        # Contar métodos de contacto
        metodo = cliente['metodo_contacto']
        metodos_contacto[metodo] = metodos_contacto.get(metodo, 0) + 1
    
    return jsonify({
        'puntuaciones': puntuaciones,
        'intereses': intereses,
        'metodos_contacto': metodos_contacto
    })

def ejecutar_en_segundo_plano(comando, script_name):
    """Ejecuta un comando en segundo plano y almacena el proceso"""
    try:
        print(f"Ejecutando comando: {comando} como {script_name}")
        # Inicializar el log para este proceso
        logs_procesos[script_name] = []
        logs_procesos[script_name].append(f"[INFO] Iniciando ejecución de {script_name} con comando: {comando}")
        
        if sys.platform == 'win32':
            # En Windows, usamos shell=True para PowerShell y scripts .ps1
            if comando.endswith('.ps1'):
                proceso = subprocess.Popen(["powershell", "-Command", f"& '{comando}'"], 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE,
                                          shell=True,
                                          cwd=os.path.dirname(comando),
                                          text=True,
                                          encoding='utf-8',
                                          errors='replace')
            else:
                proceso = subprocess.Popen(f"python {comando}", 
                                          stdout=subprocess.PIPE, 
                                          stderr=subprocess.PIPE,
                                          shell=True,
                                          cwd=os.path.dirname(comando),
                                          text=True,
                                          encoding='utf-8',
                                          errors='replace')
        else:
            # En Linux/Mac
            proceso = subprocess.Popen(comando, 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE,
                                      shell=True,
                                      cwd=os.path.dirname(comando),
                                      text=True,
                                      encoding='utf-8',
                                      errors='replace')
        
        procesos_activos[script_name] = proceso
        
        # Leer la salida para evitar bloqueos
        def leer_salida():
            while True:
                linea = proceso.stdout.readline()
                if not linea and proceso.poll() is not None:
                    break
                if linea:
                    log_entry = f"[{script_name}]: {linea.strip()}"
                    print(log_entry)
                    logs_procesos[script_name].append(log_entry)
                    # Limitar el tamaño del log
                    if len(logs_procesos[script_name]) > MAX_LOG_ENTRIES:
                        logs_procesos[script_name] = logs_procesos[script_name][-MAX_LOG_ENTRIES:]
            
            # Leer también el error estándar
            for linea in proceso.stderr:
                if linea:
                    log_entry = f"[{script_name} ERROR]: {linea.strip()}"
                    print(log_entry)
                    logs_procesos[script_name].append(log_entry)
            
            # Registrar código de salida
            codigo_salida = proceso.poll()
            log_entry = f"[{script_name}] Proceso finalizado con código de salida: {codigo_salida}"
            print(log_entry)
            logs_procesos[script_name].append(log_entry)
                
            # Al finalizar, recargar los datos
            if codigo_salida == 0:
                print(f"Proceso {script_name} finalizado correctamente. Recargando datos...")
                logs_procesos[script_name].append(f"[INFO] Recargando datos después de ejecución exitosa")
                cargar_clientes(forzar_recarga=True)
        
        # Iniciar hilo para leer la salida
        threading.Thread(target=leer_salida, daemon=True).start()
        
        return True
    except Exception as e:
        error_msg = f"Error al ejecutar {script_name}: {str(e)}"
        print(error_msg)
        if script_name in logs_procesos:
            logs_procesos[script_name].append(f"[ERROR] {error_msg}")
        traceback.print_exc()  # Imprimir el traceback completo para depuración
        return False

# Convertir la ruta a absoluta (necesario para algunos scripts)
def ruta_absoluta(ruta_relativa):
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ruta_relativa)

# Rutas de scripts disponibles
SCRIPTS_DISPONIBLES = {
    'procesar_leads': ruta_absoluta('procesar_leads.py'),
    'monitor_leads': ruta_absoluta('monitor_leads.py'),
    'run_all': ruta_absoluta('run_all.ps1'),
    'run_ovb': ruta_absoluta('run_ovb.ps1'),
    'run_dbgpt': ruta_absoluta('run_dbgpt.ps1')
}

@app.route('/ejecutar-script', methods=['GET', 'POST'])
def ejecutar_script_param():
    """Ruta para ejecutar scripts desde el dashboard usando parámetros"""
    script = request.args.get('script')
    
    if not script:
        mensaje = "No se especificó ningún script para ejecutar"
        flash(mensaje, "danger")
        return jsonify({"error": mensaje, "success": False}) if request.method == 'POST' else redirect(url_for('index'))
    
    return _ejecutar_script_interno(script)

@app.route('/ejecutar/<script>', methods=['GET', 'POST'])
@app.route('/ejecutar_script/<script>', methods=['GET', 'POST'])
def ejecutar_script(script):
    """Ruta para ejecutar scripts desde el dashboard usando URL"""
    return _ejecutar_script_interno(script)

def _ejecutar_script_interno(script):
    """Función común para ejecutar scripts"""
    print(f"Solicitud para ejecutar script: {script}")
    
    if script in SCRIPTS_DISPONIBLES:
        ruta_script = SCRIPTS_DISPONIBLES[script]
        print(f"Ruta del script a ejecutar: {ruta_script}")
        
        # Verificar si el archivo existe
        if not os.path.exists(ruta_script):
            mensaje = f"¡Error! El script {script} no se encuentra en la ruta {ruta_script}."
            flash(mensaje, "danger")
            return jsonify({"error": mensaje, "success": False}) if request.method == 'POST' else redirect(url_for('index'))
            
        # Verificar si el script ya está en ejecución
        if script in procesos_activos and procesos_activos[script].poll() is None:
            mensaje = f"El script {script} ya está en ejecución."
            flash(mensaje, "warning")
            respuesta = {"mensaje": mensaje, "success": False}
        else:
            # Ejecutar el script en segundo plano
            if ejecutar_en_segundo_plano(ruta_script, script):
                mensaje = f"Script {script} iniciado correctamente en segundo plano."
                flash(mensaje, "success")
                respuesta = {"mensaje": mensaje, "success": True}
            else:
                mensaje = f"Error al iniciar el script {script}. Revise los logs para más detalles."
                flash(mensaje, "danger")
                respuesta = {"error": mensaje, "success": False}
    else:
        mensaje = f"Script {script} no reconocido. Scripts disponibles: {', '.join(SCRIPTS_DISPONIBLES.keys())}"
        flash(mensaje, "danger")
        respuesta = {"error": mensaje, "success": False}
    
    # Si es una solicitud POST o AJAX, devolver JSON
    if request.method == 'POST' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(respuesta)
    
    # Para solicitudes normales GET, redirigir a la página principal
    return redirect(url_for('index', _=int(time.time())))

@app.route('/estado-scripts')
def estado_scripts():
    """Devuelve el estado de los scripts en ejecución"""
    estado = {}
    
    for nombre, proceso in list(procesos_activos.items()):
        codigo_salida = proceso.poll()
        
        # Si el proceso ha terminado hace más de 5 minutos, lo eliminamos
        if codigo_salida is not None:
            estado[nombre] = {
                'activo': False,
                'codigo_salida': codigo_salida
            }
        else:
            estado[nombre] = {
                'activo': True,
                'codigo_salida': None
            }
    
    return jsonify(estado)

@app.route('/logs/<script>')
def obtener_logs(script):
    """Devuelve los logs de un script específico"""
    if script in logs_procesos:
        return jsonify({
            'script': script,
            'logs': logs_procesos[script]
        })
    else:
        return jsonify({
            'script': script,
            'logs': []
        }), 404

@app.route('/logs')
def obtener_todos_logs():
    """Devuelve todos los logs disponibles"""
    return jsonify(logs_procesos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False) 