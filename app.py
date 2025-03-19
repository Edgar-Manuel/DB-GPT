from flask import Flask, render_template, jsonify
import json
import sys
import os

# Añadir el directorio padre al path para poder importar clientes_actuales
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from clientes_actuales import clientes

app = Flask(__name__)

@app.route('/')
def index():
    # Estadísticas generales
    total_clientes = len(clientes)
    clientes_alta_puntuacion = len([c for c in clientes if c['puntuacion'] >= 35])
    productos_populares = {}
    
    for cliente in clientes:
        for interes in cliente.get('intereses', []):
            productos_populares[interes] = productos_populares.get(interes, 0) + 1
    
    top_productos = sorted(productos_populares.items(), key=lambda x: x[1], reverse=True)[:5]
    
    stats = {
        'total_clientes': total_clientes,
        'clientes_premium': clientes_alta_puntuacion,
        'porcentaje_premium': round((clientes_alta_puntuacion/total_clientes)*100, 1),
        'top_productos': top_productos
    }
    
    # Top 10 clientes
    top_clientes = sorted(clientes, key=lambda x: (x['puntuacion'], len(x.get('intereses', []))), reverse=True)[:10]
    
    return render_template('index.html', stats=stats, top_clientes=top_clientes)

@app.route('/api/clientes')
def get_clientes():
    return jsonify(clientes)

@app.route('/api/stats')
def get_stats():
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 