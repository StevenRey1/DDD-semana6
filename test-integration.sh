#!/bin/bash

# Script para pruebas de integración entre Referidos y Notificaciones
# Levanta toda la infraestructura compartida

set -e

echo "🚀 Iniciando Pruebas de Integración - Referidos & Notificaciones"
echo "================================================================="

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  up       - Levantar toda la infraestructura"
    echo "  down     - Bajar toda la infraestructura" 
    echo "  restart  - Reiniciar toda la infraestructura"
    echo "  logs     - Ver logs de todos los servicios"
    echo "  test     - Ejecutar prueba de flujo completo"
    echo "  status   - Ver estado de los servicios"
    echo "  clean    - Limpiar volúmenes y redes"
    echo "  help     - Mostrar esta ayuda"
    echo ""
    echo "Puertos expuestos:"
    echo "  - PostgreSQL: 5434"
    echo "  - Pulsar: 6653 (broker), 8083 (admin), 8084 (web)"  
    echo "  - Referidos: 5001"
    echo "  - Notificaciones: 8002"
    echo "  - Pulsar Manager: 9529"
}

# Función para verificar estado de servicios
check_status() {
    echo "📊 Estado de los servicios:"
    echo "----------------------------"
    
    # Verificar PostgreSQL
    if curl -s http://localhost:5434 >/dev/null 2>&1; then
        echo "✅ PostgreSQL: Disponible en puerto 5434"
    else
        echo "❌ PostgreSQL: No disponible"
    fi
    
    # Verificar Pulsar
    if curl -s http://localhost:8083/admin/v2/clusters >/dev/null 2>&1; then
        echo "✅ Pulsar: Disponible en puerto 8083"
    else
        echo "❌ Pulsar: No disponible"
    fi
    
    # Verificar Referidos
    if curl -s http://localhost:5001/health >/dev/null 2>&1; then
        echo "✅ Referidos: Disponible en puerto 5001"
    else
        echo "❌ Referidos: No disponible"
    fi
    
    # Verificar Notificaciones
    if curl -s http://localhost:8002/health >/dev/null 2>&1; then
        echo "✅ Notificaciones: Disponible en puerto 8002"
    else
        echo "❌ Notificaciones: No disponible"
    fi
    
    echo ""
}

# Función para prueba de flujo completo
run_test() {
    echo "🧪 Ejecutando prueba de flujo completo..."
    echo "=========================================="
    
    # Verificar que los servicios estén disponibles
    echo "1. Verificando servicios..."
    check_status
    
    echo "2. Ejecutando script de prueba..."
    if [ -f "enviar_evento_test.py" ]; then
        cd src/referidos
        python ../../enviar_evento_test.py
        cd ../..
    else
        echo "❌ Script de prueba no encontrado"
        return 1
    fi
    
    echo "3. Verificando logs de procesamiento..."
    sleep 3
    
    echo "--- Logs de Referidos (últimas 10 líneas) ---"
    docker logs referidos-shared --tail 10
    
    echo ""
    echo "--- Logs de Notificaciones (últimas 10 líneas) ---"
    docker logs notificaciones-shared --tail 10
    
    echo ""
    echo "4. Verificando health checks..."
    echo "Referidos:"
    curl -s http://localhost:5001/health | python -m json.tool
    echo ""
    echo "Notificaciones:"
    curl -s http://localhost:8002/health | python -m json.tool
}

# Procesar comando
case "${1:-up}" in
    "up")
        echo "⬆️  Levantando infraestructura..."
        docker-compose -f docker-compose.integration.yml up -d
        echo ""
        echo "⏳ Esperando a que los servicios estén listos..."
        sleep 15
        check_status
        echo ""
        echo "🎉 ¡Infraestructura lista para pruebas!"
        echo "💡 Ejecuta '$0 test' para probar el flujo completo"
        ;;
    "down")
        echo "⬇️  Bajando infraestructura..."
        docker-compose -f docker-compose.integration.yml down
        ;;
    "restart")
        echo "🔄 Reiniciando infraestructura..."
        docker-compose -f docker-compose.integration.yml restart
        sleep 10
        check_status
        ;;
    "logs")
        echo "📋 Logs de todos los servicios:"
        docker-compose -f docker-compose.integration.yml logs -f
        ;;
    "test")
        run_test
        ;;
    "status")
        check_status
        ;;
    "clean")
        echo "🧹 Limpiando volúmenes y redes..."
        docker-compose -f docker-compose.integration.yml down -v
        docker network prune -f
        docker volume prune -f
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo "❌ Comando no reconocido: $1"
        show_help
        exit 1
        ;;
esac