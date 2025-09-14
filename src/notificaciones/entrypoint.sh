#!/bin/bash
set -e

echo "🚀 Iniciando Microservicio de Notificaciones..."
echo "   Ambiente: ${AMBIENTE:-desarrollo}"
echo "   Debug: ${DEBUG:-false}"
echo "   Log Level: ${LOG_LEVEL:-INFO}"

# Función para esperar servicios
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    
    echo "⏳ Esperando a que $service_name esté disponible en $host:$port..."
    
    for i in {1..60}; do
        if nc -z "$host" "$port" 2>/dev/null; then
            echo "✅ $service_name está disponible!"
            return 0
        fi
        echo "   Intento $i/60: $service_name no disponible, esperando..."
        sleep 2
    done
    
    echo "❌ Timeout esperando $service_name en $host:$port"
    return 1
}

# Esperar servicios si está habilitado
if [ "${WAIT_FOR_SERVICES:-true}" = "true" ]; then
    # Esperar PostgreSQL
    if [ -n "${POSTGRES_HOST:-postgres}" ]; then
        wait_for_service "${POSTGRES_HOST:-postgres}" "5432" "PostgreSQL"
    fi
    
    # Esperar Pulsar
    if [ -n "${PULSAR_HOST:-pulsar}" ]; then
        wait_for_service "${PULSAR_HOST:-pulsar}" "${PULSAR_PORT:-6650}" "Pulsar"
    fi
fi

echo "🎯 Configuración del microservicio de notificaciones:"
echo "   FastAPI: 0.0.0.0:${PORT:-8002}"
echo "   Pulsar: ${PULSAR_HOST:-pulsar}:${PULSAR_PORT:-6650}"
echo "   Base de datos: ${DATABASE_URL:-PostgreSQL local}"
echo "   Canales habilitados:"
echo "     - Email: ${EMAIL_HABILITADO:-true}"
echo "     - SMS: ${SMS_HABILITADO:-true}"
echo "     - Push: ${PUSH_HABILITADO:-true}"

echo "📊 Base de datos PostgreSQL configurada"

echo "🔥 Iniciando aplicación FastAPI..."

# Ejecutar el comando pasado como argumentos
exec "$@"