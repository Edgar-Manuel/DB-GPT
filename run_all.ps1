# Script para ejecutar todo el proceso de OVB
Write-Host "=== Iniciando proceso completo de OVB ==="

# 1. Procesar leads iniciales
Write-Host "[1/3] Procesando leads iniciales..."
python procesar_leads.py

# 2. Iniciar monitor de leads en segundo plano
Write-Host "[2/3] Iniciando monitor de leads en segundo plano..."
Start-Process python -ArgumentList "monitor_leads.py" -WindowStyle Hidden

# 3. Ejecutar sistema OVB
Write-Host "[3/3] Iniciando sistema OVB..."
.\run_ovb.ps1

Write-Host "=== Proceso completo iniciado exitosamente ===" 