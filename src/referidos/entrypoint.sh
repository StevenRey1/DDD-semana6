#!/bin/bash
set -e

echo "🚀 Iniciando Microservicio de Referidos..."
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
    if [ -n "${DB_HOST}" ] && [ -n "${DB_PORT}" ]; then
        wait_for_service "${DB_HOST}" "${DB_PORT}" "PostgreSQL"
    fi
    
    # Esperar Pulsar
    if [ -n "${PULSAR_HOST}" ] && [ -n "${PULSAR_PORT}" ]; then
        wait_for_service "${PULSAR_HOST}" "${PULSAR_PORT}" "Pulsar"
    fi
fi

echo "🎯 Configuración del microservicio de referidos:"
echo "   Flask: ${FLASK_HOST:-0.0.0.0}:${FLASK_PORT:-5001}"
echo "   Pulsar: ${PULSAR_HOST:-localhost}:${PULSAR_PORT:-6650}"
echo "   Base de datos: ${DATABASE_URL:-PostgreSQL local}"
echo "   Eventos habilitados: ${EVENTOS_HABILITADOS:-true}"

echo "📊 Base de datos PostgreSQL configurada"

echo "🔥 Iniciando aplicación Flask..."

# Ejecutar el comando pasado como argumentos
exec "$@"