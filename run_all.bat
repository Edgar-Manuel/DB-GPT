@echo off
echo === Iniciando proceso completo de OVB ===

:: 1. Procesar leads iniciales
echo [1/3] Procesando leads iniciales...
python procesar_leads.py

:: 2. Iniciar monitor de leads en segundo plano
echo [2/3] Iniciando monitor de leads en segundo plano...
start /min python monitor_leads.py

:: 3. Ejecutar sistema OVB
echo [3/3] Iniciando sistema OVB...
call run_ovb.ps1

echo === Proceso completo iniciado exitosamente ===
pause 