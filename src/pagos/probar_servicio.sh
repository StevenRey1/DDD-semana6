#!/bin/bash

# Script para levantar y probar el servicio de Pagos completo
# Uso: ./probar_servicio.sh [comando]
# Comandos: start, test, stop, restart, logs, status

set -e

# Configuración
COMPOSE_FILE="docker-compose.dev.yml"
SERVICE_NAME="pagos"
API_URL="http://localhost:8090"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# Verificar si Docker está disponible
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker no está instalado o no está en PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose no está instalado o no está en PATH"
        exit 1
    fi
}

# Levantar servicios
start_services() {
    log "Levantando servicios de Pagos..."
    
    # Construir y levantar servicios
    docker-compose -f $COMPOSE_FILE build
    docker-compose -f $COMPOSE_FILE up -d
    
    success "Servicios iniciados"
    
    # Esperar a que estén disponibles
    wait_for_services
}

# Esperar a que los servicios estén disponibles
wait_for_services() {
    log "Esperando a que los servicios estén disponibles..."
    
    # Esperar base de datos
    log "Esperando PostgreSQL..."
    for i in {1..30}; do
        if docker-compose -f $COMPOSE_FILE exec -T postgres-pagos pg_isready -U postgres &>/dev/null; then
            success "PostgreSQL disponible"
            break
        fi
        if [ $i -eq 30 ]; then
            error "PostgreSQL no disponible después de 30 intentos"
            exit 1
        fi
        sleep 2
    done
    
    # Esperar Pulsar
    log "Esperando Pulsar..."
    for i in {1..30}; do
        if docker-compose -f $COMPOSE_FILE logs pulsar | grep -q "messaging service is ready" &>/dev/null; then
            success "Pulsar disponible"
            break
        fi
        if [ $i -eq 30 ]; then
            warning "Pulsar puede no estar completamente disponible"
            break
        fi
        sleep 2
    done
    
    # Esperar API
    log "Esperando API de Pagos..."
    for i in {1..60}; do
        if curl -s "$API_URL/health" &>/dev/null; then
            success "API de Pagos disponible en $API_URL"
            break
        fi
        if [ $i -eq 60 ]; then
            error "API no disponible después de 60 intentos"
            show_logs
            exit 1
        fi
        sleep 2
    done
    
    success "Todos los servicios están disponibles"
}

# Ejecutar tests
run_tests() {
    log "Ejecutando validación del servicio..."
    
    # Verificar que los servicios estén corriendo
    if ! curl -s "$API_URL/health" &>/dev/null; then
        error "API no está disponible. Ejecuta primero: $0 start"
        exit 1
    fi
    
    # Ejecutar script de validación
    if [ -f "script_validacion.py" ]; then
        log "Ejecutando script de validación..."
        python script_validacion.py --skip-tests
    else
        warning "Script de validación no encontrado, ejecutando tests básicos..."
        run_basic_tests
    fi
}

# Tests básicos si no está el script de validación
run_basic_tests() {
    log "Ejecutando tests básicos..."
    
    # Test 1: Health check
    log "Test 1: Health check..."
    if curl -s "$API_URL/health" | grep -q "ok" &>/dev/null; then
        success "Health check OK"
    else
        error "Health check falló"
        return 1
    fi
    
    # Test 2: Crear pago
    log "Test 2: Crear pago..."
    TRANSACTION_ID="test_$(date +%s)"
    RESPONSE=$(curl -s -X POST "$API_URL/pagos" \
        -H "Content-Type: application/json" \
        -d "{
            \"comando\": \"Iniciar\",
            \"data\": {
                \"idTransaction\": \"$TRANSACTION_ID\",
                \"estado\": \"PENDING\",
                \"valor\": 100.0,
                \"fechaCreacion\": \"$(date -Iseconds)\",
                \"fechaActualizacion\": \"$(date -Iseconds)\",
                \"idUsuario\": \"test_user\"
            }
        }")
    
    if echo "$RESPONSE" | grep -q "$TRANSACTION_ID"; then
        success "Crear pago OK"
    else
        error "Crear pago falló: $RESPONSE"
        return 1
    fi
    
    # Test 3: Consultar pago
    log "Test 3: Consultar pago..."
    sleep 2  # Dar tiempo para procesamiento
    RESPONSE=$(curl -s "$API_URL/pagos/$TRANSACTION_ID")
    
    if echo "$RESPONSE" | grep -q "$TRANSACTION_ID"; then
        success "Consultar pago OK"
    else
        error "Consultar pago falló: $RESPONSE"
        return 1
    fi
    
    success "Todos los tests básicos pasaron"
}

# Mostrar logs
show_logs() {
    log "Mostrando logs de los servicios..."
    docker-compose -f $COMPOSE_FILE logs --tail=50
}

# Mostrar estado de servicios
show_status() {
    log "Estado de los servicios:"
    docker-compose -f $COMPOSE_FILE ps
    
    echo
    log "Verificando conectividad:"
    
    # API
    if curl -s "$API_URL/health" &>/dev/null; then
        success "API disponible en $API_URL"
    else
        error "API no disponible en $API_URL"
    fi
    
    # Base de datos
    if docker-compose -f $COMPOSE_FILE exec -T postgres-pagos pg_isready -U postgres &>/dev/null; then
        success "PostgreSQL disponible"
    else
        error "PostgreSQL no disponible"
    fi
}

# Parar servicios
stop_services() {
    log "Parando servicios..."
    docker-compose -f $COMPOSE_FILE down
    success "Servicios parados"
}

# Reiniciar servicios
restart_services() {
    log "Reiniciando servicios..."
    stop_services
    start_services
}

# Limpiar todo (incluye volúmenes)
clean_all() {
    log "Limpiando todo (servicios, volúmenes, imágenes)..."
    docker-compose -f $COMPOSE_FILE down -v --rmi all
    success "Limpieza completa"
}

# Mostrar ayuda
show_help() {
    echo "Uso: $0 [comando]"
    echo
    echo "Comandos disponibles:"
    echo "  start     - Levantar todos los servicios"
    echo "  test      - Ejecutar tests de validación"
    echo "  stop      - Parar todos los servicios"
    echo "  restart   - Reiniciar todos los servicios"
    echo "  logs      - Mostrar logs de servicios"
    echo "  status    - Mostrar estado de servicios"
    echo "  clean     - Limpiar todo (servicios, volúmenes, imágenes)"
    echo "  help      - Mostrar esta ayuda"
    echo
    echo "Ejemplos:"
    echo "  $0 start && $0 test    # Levantar y probar"
    echo "  $0 logs                # Ver logs"
    echo "  $0 status              # Ver estado"
}

# Script principal
main() {
    check_docker
    
    case "${1:-help}" in
        start)
            start_services
            ;;
        test)
            run_tests
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        clean)
            clean_all
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Comando desconocido: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Verificar que estamos en el directorio correcto
if [ ! -f "$COMPOSE_FILE" ]; then
    error "No se encontró $COMPOSE_FILE en el directorio actual"
    error "Ejecuta este script desde el directorio src/pagos/"
    exit 1
fi

# Ejecutar función principal
main "$@"