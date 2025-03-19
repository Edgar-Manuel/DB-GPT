"""
Sistema de AutomatizaciÃ³n de Ventas OVB - VersiÃ³n ProducciÃ³n
Este script procesa leads reales y genera recomendaciones personalizadas.
"""

import json
from typing import Dict, List, Any
from datetime import datetime
from clientes_actuales import obtener_clientes

def generar_recomendacion_unica(cliente: Dict[str, Any]) -> List[Dict[str, str]]:
    """Genera recomendaciones Ãºnicas basadas en el perfil especÃ­fico del cliente"""
    recomendaciones = []
    
    # AnÃ¡lisis del perfil financiero
    nombre = cliente.get('nombre', '')
    ubicacion = cliente.get('ubicacion', '')
    intereses = cliente.get('intereses', [])
    historial = cliente.get('historial_compras', [])
    potencial = cliente.get('potencial_inversion', 'bajo')
    puntuacion = cliente.get('puntuacion', 0)
    
    # Recomendaciones basadas en puntuaciÃ³n y potencial
    if puntuacion >= 35 or potencial == 'alto':
        recomendaciones.append({
            'producto': f'Plan InversiÃ³n Premium {ubicacion}',
            'prioridad': 'alta',
            'razon': f'Perfil de alto valor con puntuaciÃ³n destacada de {puntuacion}',
            'beneficio': 'Acceso a productos financieros exclusivos con ventajas fiscales premium'
        })
    elif 20 <= puntuacion < 35:
        recomendaciones.append({
            'producto': f'Plan ProtecciÃ³n Integral Plus',
            'prioridad': 'media',
            'razon': 'Perfil equilibrado con potencial de crecimiento',
            'beneficio': 'Cobertura completa adaptada a tus necesidades actuales y futuras'
        })
    else:
        recomendaciones.append({
            'producto': 'Plan Inicial Flexible',
            'prioridad': 'media',
            'razon': 'Inicio en la planificaciÃ³n financiera',
            'beneficio': 'SoluciÃ³n adaptable que crece contigo y tus necesidades'
        })

    # Recomendaciones personalizadas basadas en intereses
    for interes in intereses:
        producto_base = ''
        if 'inversiÃ³n' in interes.lower() or 'ahorro' in interes.lower():
            producto_base = f'Fondo {interes.title()}'
        elif 'seguro' in interes.lower():
            producto_base = f'Seguro {interes.title()}'
        elif 'jubilaciÃ³n' in interes.lower() or 'pensiones' in interes.lower():
            producto_base = f'Plan Pensiones {interes.title()}'
        elif 'patrimonial' in interes.lower():
            producto_base = f'GestiÃ³n Patrimonial {interes.title()}'
        
        if producto_base and producto_base not in [r['producto'] for r in recomendaciones]:
            recomendaciones.append({
                'producto': f'{producto_base} Personalizado',
                'prioridad': 'alta' if potencial == 'alto' else 'media',
                'razon': f'Alineado con tu interÃ©s especÃ­fico en {interes}',
                'beneficio': f'SoluciÃ³n especializada para tus objetivos en {interes}'
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
    """Ejecuta la campaÃ±a de marketing con datos reales de todos los clientes"""
    try:
        clientes = obtener_clientes()
        total_clientes = len(clientes)
        
        print("\nðŸš€ SISTEMA OVB - CAMPAÃ‘A DE MARKETING REAL")
        print(f"ðŸ“Š Total clientes a procesar: {total_clientes}")
        print(f"â±ï¸ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        for i, cliente in enumerate(clientes, 1):
            print(f"\n{'='*80}")
            print(f"ðŸ‘¤ Cliente {i}/{total_clientes}")
            print(f"ðŸ“‹ Datos principales:")
            print(f"   Nombre: {cliente['nombre']} (ID: {cliente['id']})")
            print(f"   MÃ©todo contacto: {cliente['metodo_contacto']}")
            if cliente.get('telefono'):
                print(f"   TelÃ©fono: {cliente['telefono']}")
            print(f"   Correo: {cliente['correo']}")
            print(f"   PuntuaciÃ³n: {cliente['puntuacion']}")
            print(f"   Potencial: {cliente['potencial_inversion']}")
            
            if cliente.get('intereses'):
                print(f"   Intereses: {', '.join(cliente['intereses'])}")
            if cliente.get('historial_compras'):
                print(f"   Productos actuales: {', '.join(cliente['historial_compras'])}")
            
            recomendaciones = generar_recomendacion_unica(cliente)
            
            print("\nðŸ“ˆ RECOMENDACIONES PERSONALIZADAS:")
            for idx, rec in enumerate(recomendaciones, 1):
                print(f"\n{idx}. {rec['producto']}")
                print(f"   Prioridad: {rec['prioridad'].upper()}")
                print(f"   âž¤ RazÃ³n: {rec['razon']}")
                print(f"   âœ“ Beneficio: {rec['beneficio']}")
            
            print(f"\nâœ… Procesado: {datetime.now().strftime('%H:%M:%S')}")
            
    except Exception as e:
        print(f"âŒ Error en la ejecuciÃ³n: {str(e)}")
        raise

if __name__ == "__main__":
    print("\n=== SISTEMA OVB - VERSIÃ“N PRODUCCIÃ“N 2.0 ===")
    ejecutar_campana_real() 
