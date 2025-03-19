# Script para iniciar DB-GPT con OVB

# Establecer variables de entorno
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

# Ejecutar el script de OVB
Write-Host "Iniciando Sistema de Automatización de Ventas de OVB..." -ForegroundColor Green
python ovb_sales_agents.py 