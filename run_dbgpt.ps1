# Script para iniciar DB-GPT con las variables de entorno necesarias

# Establecer variables de entorno para la sesión actual
$env:OPENAI_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlZG1jMm1pbDI0QGdtYWlsLmNvbSIsImlhdCI6MTczNzM1OTA5Mn0.qmBSFjyeXknXFmP9zcNkCtBCOd6IxKIAb_3vBCX8INA"
$env:OPENAI_API_BASE = "https://api.hyperbolic.xyz/v1"
$env:LLM_MODEL_NAME = "Qwen/QwQ-32B"
$env:LLM_MODEL_PROVIDER = "proxy/openai"
$env:EMBEDDING_MODEL_NAME = "Qwen/QwQ-32B"
$env:EMBEDDING_MODEL_PROVIDER = "proxy/openai"
$env:EMBEDDING_MODEL_API_URL = "https://api.hyperbolic.xyz/v1/embeddings"
$env:LANGUAGE = "es"
$env:DBGPT_LANG = "es"

# Mostrar las variables establecidas
Write-Host "Variables de entorno configuradas:" -ForegroundColor Green
Write-Host "API_KEY: $env:OPENAI_API_KEY"
Write-Host "API_BASE: $env:OPENAI_API_BASE"
Write-Host "MODEL_NAME: $env:LLM_MODEL_NAME"
Write-Host "MODEL_PROVIDER: $env:LLM_MODEL_PROVIDER"
Write-Host "LANGUAGE: $env:LANGUAGE"

# Determinar la ruta completa del directorio actual
$currentDir = Get-Location

# Comando a ejecutar
$commandToRun = "cd '$currentDir'; Write-Host 'Iniciando DB-GPT Dashboard...' -ForegroundColor Cyan; uv run dbgpt start webserver --config configs/dbgpt-proxy-openai.toml"

# Configurar las variables de entorno para el proceso hijo
$processStartInfo = New-Object System.Diagnostics.ProcessStartInfo
$processStartInfo.FileName = "powershell.exe"
$processStartInfo.Arguments = "-NoExit", "-Command", 
    "& {
        # Configurar variables de entorno
        `$env:OPENAI_API_KEY = '$env:OPENAI_API_KEY'
        `$env:OPENAI_API_BASE = '$env:OPENAI_API_BASE'
        `$env:LLM_MODEL_NAME = '$env:LLM_MODEL_NAME'
        `$env:LLM_MODEL_PROVIDER = '$env:LLM_MODEL_PROVIDER'
        `$env:EMBEDDING_MODEL_NAME = '$env:EMBEDDING_MODEL_NAME'
        `$env:EMBEDDING_MODEL_PROVIDER = '$env:EMBEDDING_MODEL_PROVIDER'
        `$env:EMBEDDING_MODEL_API_URL = '$env:EMBEDDING_MODEL_API_URL'
        `$env:LANGUAGE = '$env:LANGUAGE'
        `$env:DBGPT_LANG = '$env:DBGPT_LANG'
        
        # Cambiar al directorio correcto
        Set-Location '$currentDir'
        
        # Mostrar información
        Write-Host 'DB-GPT Dashboard - Variables configuradas' -ForegroundColor Cyan
        Write-Host 'Iniciando DB-GPT en: $currentDir' -ForegroundColor Yellow
        
        # Ejecutar DB-GPT
        uv run dbgpt start webserver --config configs/dbgpt-proxy-openai.toml
    }"

# Crear una nueva ventana de consola
$processStartInfo.UseShellExecute = $true
$processStartInfo.CreateNoWindow = $false
$processStartInfo.WindowStyle = 'Normal'

# Iniciar el proceso
Write-Host "Iniciando DB-GPT en una nueva ventana..." -ForegroundColor Green
[System.Diagnostics.Process]::Start($processStartInfo)

# Informar al usuario
Write-Host "Se ha abierto una nueva ventana con el dashboard de DB-GPT" -ForegroundColor Cyan
Write-Host "Si no ves la ventana, revisa en la barra de tareas o Alt+Tab" -ForegroundColor Yellow
Write-Host "El dashboard estará disponible en: http://localhost:5000" -ForegroundColor Green 