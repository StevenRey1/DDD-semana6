# Script para pruebas de integración entre Referidos y Notificaciones
# Levanta toda la infraestructura compartida

param(
    [Parameter(Position=0)]
    [string]$Command = "up"
)

Write-Host "🚀 Iniciando Pruebas de Integración - Referidos & Notificaciones" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green

function Show-Help {
    Write-Host "Uso: .\test-integration.ps1 [comando]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Comandos disponibles:" -ForegroundColor Cyan
    Write-Host "  up       - Levantar toda la infraestructura"
    Write-Host "  down     - Bajar toda la infraestructura" 
    Write-Host "  restart  - Reiniciar toda la infraestructura"
    Write-Host "  logs     - Ver logs de todos los servicios"
    Write-Host "  test     - Ejecutar prueba de flujo completo"
    Write-Host "  status   - Ver estado de los servicios"
    Write-Host "  clean    - Limpiar volúmenes y redes"
    Write-Host "  help     - Mostrar esta ayuda"
    Write-Host ""
    Write-Host "Puertos expuestos:" -ForegroundColor Magenta
    Write-Host "  - PostgreSQL: 5434"
    Write-Host "  - Pulsar: 6653 (broker), 8083 (admin), 8084 (web)"  
    Write-Host "  - Referidos: 5001"
    Write-Host "  - Notificaciones: 8002"
    Write-Host "  - Pulsar Manager: 9529"
}

function Check-Status {
    Write-Host "📊 Estado de los servicios:" -ForegroundColor Blue
    Write-Host "----------------------------"
    
    # Verificar Pulsar
    try {
        $pulsar = Invoke-WebRequest -Uri "http://localhost:8083/admin/v2/clusters" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "✅ Pulsar: Disponible en puerto 8083" -ForegroundColor Green
    } catch {
        Write-Host "❌ Pulsar: No disponible" -ForegroundColor Red
    }
    
    # Verificar Referidos
    try {
        $referidos = Invoke-WebRequest -Uri "http://localhost:5001/health" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "✅ Referidos: Disponible en puerto 5001" -ForegroundColor Green
    } catch {
        Write-Host "❌ Referidos: No disponible" -ForegroundColor Red
    }
    
    # Verificar Notificaciones
    try {
        $notificaciones = Invoke-WebRequest -Uri "http://localhost:8002/health" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "✅ Notificaciones: Disponible en puerto 8002" -ForegroundColor Green
    } catch {
        Write-Host "❌ Notificaciones: No disponible" -ForegroundColor Red
    }
    
    Write-Host ""
}

function Run-Test {
    Write-Host "🧪 Ejecutando prueba de flujo completo..." -ForegroundColor Blue
    Write-Host "=========================================="
    
    # Verificar que los servicios estén disponibles
    Write-Host "1. Verificando servicios..."
    Check-Status
    
    Write-Host "2. Ejecutando script de prueba..."
    if (Test-Path "enviar_evento_test.py") {
        Push-Location "src\referidos"
        try {
            python "..\..\enviar_evento_test.py"
        } catch {
            Write-Host "❌ Error ejecutando script de prueba: $_" -ForegroundColor Red
            Pop-Location
            return
        }
        Pop-Location
    } else {
        Write-Host "❌ Script de prueba no encontrado" -ForegroundColor Red
        return
    }
    
    Write-Host "3. Verificando logs de procesamiento..."
    Start-Sleep -Seconds 3
    
    Write-Host "--- Logs de Referidos (últimas 10 líneas) ---" -ForegroundColor Yellow
    docker logs referidos-shared --tail 10
    
    Write-Host ""
    Write-Host "--- Logs de Notificaciones (últimas 10 líneas) ---" -ForegroundColor Yellow
    docker logs notificaciones-shared --tail 10
    
    Write-Host ""
    Write-Host "4. Verificando health checks..."
    Write-Host "Referidos:" -ForegroundColor Cyan
    try {
        $referidosHealth = Invoke-WebRequest -Uri "http://localhost:5001/health" -ErrorAction Stop
        $referidosHealth.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
    } catch {
        Write-Host "❌ Error obteniendo health de referidos" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Notificaciones:" -ForegroundColor Cyan
    try {
        $notificacionesHealth = Invoke-WebRequest -Uri "http://localhost:8002/health" -ErrorAction Stop
        $notificacionesHealth.Content | ConvertFrom-Json | ConvertTo-Json -Depth 3
    } catch {
        Write-Host "❌ Error obteniendo health de notificaciones" -ForegroundColor Red
    }
}

# Procesar comando
switch ($Command.ToLower()) {
    "up" {
        Write-Host "⬆️  Levantando infraestructura..." -ForegroundColor Blue
        docker-compose -f docker-compose.integration.yml up -d
        Write-Host ""
        Write-Host "⏳ Esperando a que los servicios estén listos..." -ForegroundColor Yellow
        Start-Sleep -Seconds 15
        Check-Status
        Write-Host ""
        Write-Host "🎉 ¡Infraestructura lista para pruebas!" -ForegroundColor Green
        Write-Host "💡 Ejecuta '.\test-integration.ps1 test' para probar el flujo completo" -ForegroundColor Cyan
    }
    "down" {
        Write-Host "⬇️  Bajando infraestructura..." -ForegroundColor Blue
        docker-compose -f docker-compose.integration.yml down
    }
    "restart" {
        Write-Host "🔄 Reiniciando infraestructura..." -ForegroundColor Blue
        docker-compose -f docker-compose.integration.yml restart
        Start-Sleep -Seconds 10
        Check-Status
    }
    "logs" {
        Write-Host "📋 Logs de todos los servicios:" -ForegroundColor Blue
        docker-compose -f docker-compose.integration.yml logs -f
    }
    "test" {
        Run-Test
    }
    "status" {
        Check-Status
    }
    "clean" {
        Write-Host "🧹 Limpiando volúmenes y redes..." -ForegroundColor Blue
        docker-compose -f docker-compose.integration.yml down -v
        docker network prune -f
        docker volume prune -f
    }
    { $_ -in "help", "-h", "--help" } {
        Show-Help
    }
    default {
        Write-Host "❌ Comando no reconocido: $Command" -ForegroundColor Red
        Show-Help
        exit 1
    }
}