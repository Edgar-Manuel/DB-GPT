"""
Script para refrescar los datos del dashboard.
Este script simplemente toca el archivo clientes_actuales.py para forzar una recarga.
"""

import os
import sys
import importlib
import time

def main():
    print("Verificando datos de clientes...")
    
    # Importar el módulo para verificar que existe
    try:
        # Eliminar del cache si ya existe
        if 'clientes_actuales' in sys.modules:
            del sys.modules['clientes_actuales']
        
        # Importar el módulo de nuevo
        import clientes_actuales
        
        num_clientes = len(clientes_actuales.clientes)
        print(f"Se encontraron {num_clientes} clientes en el archivo.")
        
        if num_clientes == 0:
            print("⚠️ ALERTA: No se encontraron clientes en el archivo.")
        else:
            print("✅ Datos cargados correctamente.")
            
        # Tocar el archivo para forzar recarga
        ruta_archivo = os.path.abspath(clientes_actuales.__file__)
        print(f"Archivo de clientes: {ruta_archivo}")
        
        # Actualizar la fecha de modificación
        os.utime(ruta_archivo, None)
        print("Archivo actualizado para forzar recarga en el dashboard.")
        
        print("🔁 Por favor, recarga manualmente el dashboard para ver los cambios.")
    except Exception as e:
        print(f"❌ Error al verificar datos: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main() 