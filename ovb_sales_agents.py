"""
Sistema de Automatización de Ventas OVB - Versión Producción
Este script procesa leads reales y genera recomendaciones personalizadas.
"""

import json
from typing import Dict, List, Any
from datetime import datetime
from clientes_actuales import obtener_clientes

def generar_recomendacion_unica(cliente: Dict[str, Any]) -> List[Dict[str, str]]:
    """Genera recomendaciones únicas basadas en el perfil específico del cliente"""
    recomendaciones = []
    
    # Análisis del perfil financiero
    nombre = cliente.get('nombre', '')
    ubicacion = cliente.get('ubicacion', '')
    intereses = cliente.get('intereses', [])
    historial = cliente.get('historial_compras', [])
    potencial = cliente.get('potencial_inversion', 'bajo')
    puntuacion = cliente.get('puntuacion', 0)
    
    # Recomendaciones basadas en puntuación y potencial
    if puntuacion >= 35 or potencial == 'alto':
        recomendaciones.append({
            'producto': f'Plan Inversión Premium {ubicacion}',
            'prioridad': 'alta',
            'razon': f'Perfil de alto valor con puntuación destacada de {puntuacion}',
            'beneficio': 'Acceso a productos financieros exclusivos con ventajas fiscales premium'
        })
    elif 20 <= puntuacion < 35:
        recomendaciones.append({
            'producto': f'Plan Protección Integral Plus',
            'prioridad': 'media',
            'razon': 'Perfil equilibrado con potencial de crecimiento',
            'beneficio': 'Cobertura completa adaptada a tus necesidades actuales y futuras'
        })
    else:
        recomendaciones.append({
            'producto': 'Plan Inicial Flexible',
            'prioridad': 'media',
            'razon': 'Inicio en la planificación financiera',
            'beneficio': 'Solución adaptable que crece contigo y tus necesidades'
        })

    # Recomendaciones personalizadas basadas en intereses
    for interes in intereses:
        producto_base = ''
        if 'inversión' in interes.lower() or 'ahorro' in interes.lower():
            producto_base = f'Fondo {interes.title()}'
        elif 'seguro' in interes.lower():
            producto_base = f'Seguro {interes.title()}'
        elif 'jubilación' in interes.lower() or 'pensiones' in interes.lower():
            producto_base = f'Plan Pensiones {interes.title()}'
        elif 'patrimonial' in interes.lower():
            producto_base = f'Gestión Patrimonial {interes.title()}'
        
        if producto_base and producto_base not in [r['producto'] for r in recomendaciones]:
            recomendaciones.append({
                'producto': f'{producto_base} Personalizado',
                'prioridad': 'alta' if potencial == 'alto' else 'media',
                'razon': f'Alineado con tu interés específico en {interes}',
                'beneficio': f'Solución especializada para tus objetivos en {interes}'
            })

    # Recomendaciones basadas en horario de disponibilidad
    horario = cliente.get('horario', {})
    dias_disponibles = sum(1 for dia, hora in horario.items() if hora)
    if dias_disponibles >= 4:
        recomendaciones.append({
            'producto': 'Servicio Asesoramiento Premium',
            'prioridad': 'alta',
            'razon': 'Alta disponibilidad para asesoramiento personalizado',
            'beneficio': 'Acceso prioritario a tu asesor personal en horario extendido'
        })

    # Evitar productos que ya tiene
    recomendaciones = [r for r in recomendaciones if r['producto'] not in historial]

    return recomendaciones[:3]  # Retornamos las 3 mejores recomendaciones

def ejecutar_campana_real():
    """Ejecuta la campaña de marketing con datos reales de todos los clientes"""
    try:
        clientes = obtener_clientes()
        total_clientes = len(clientes)
        
        print("\n🚀 SISTEMA OVB - CAMPAÑA DE MARKETING REAL")
        print(f"📊 Total clientes a procesar: {total_clientes}")
        print(f"⏱️ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        for i, cliente in enumerate(clientes, 1):
            print(f"\n{'='*80}")
            print(f"👤 Cliente {i}/{total_clientes}")
            print(f"📋 Datos principales:")
            print(f"   Nombre: {cliente['nombre']} (ID: {cliente['id']})")
            print(f"   Método contacto: {cliente['metodo_contacto']}")
            if cliente.get('telefono'):
                print(f"   Teléfono: {cliente['telefono']}")
            print(f"   Correo: {cliente['correo']}")
            print(f"   Puntuación: {cliente['puntuacion']}")
            print(f"   Potencial: {cliente['potencial_inversion']}")
            
            if cliente.get('intereses'):
                print(f"   Intereses: {', '.join(cliente['intereses'])}")
            if cliente.get('historial_compras'):
                print(f"   Productos actuales: {', '.join(cliente['historial_compras'])}")
            
            recomendaciones = generar_recomendacion_unica(cliente)
            
            print("\n📈 RECOMENDACIONES PERSONALIZADAS:")
            for idx, rec in enumerate(recomendaciones, 1):
                print(f"\n{idx}. {rec['producto']}")
                print(f"   Prioridad: {rec['prioridad'].upper()}")
                print(f"   ➤ Razón: {rec['razon']}")
                print(f"   ✓ Beneficio: {rec['beneficio']}")
            
            print(f"\n✅ Procesado: {datetime.now().strftime('%H:%M:%S')}")
            
    except Exception as e:
        print(f"❌ Error en la ejecución: {str(e)}")
        raise

if __name__ == "__main__":
    print("\n=== SISTEMA OVB - VERSIÓN PRODUCCIÓN 2.0 ===")
    ejecutar_campana_real()
