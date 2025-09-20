#!/bin/bash

echo "🚀 Configurando entorno de prueba para bff_web..."

# Crear tópicos necesarios
echo "📝 Creando tópicos en Pulsar..."
docker exec pulsar-test bin/pulsar-admin topics create persistent://public/default/eventos-tracking
docker exec pulsar-test bin/pulsar-admin topics create persistent://public/default/comando-tracking

echo "✅ Tópicos creados exitosamente"

# Verificar estado de servicios
echo "🔍 Verificando servicios..."
docker ps

echo ""
echo "📋 Servicios disponibles:"
echo "  🌐 UI: http://localhost:8081"
echo "  🚀 BFF API: http://localhost:8000"
echo "  📊 GraphQL: http://localhost:8000/v1/graphql"
echo "  📡 SSE Stream: http://localhost:8000/stream"
echo "  🐳 Pulsar Admin: http://localhost:8080"

echo ""
echo "🧪 Para probar:"
echo "1. Abrir http://localhost:8081 en el navegador"
echo "2. Llenar el formulario y crear un evento"
echo "3. Ver el evento aparecer en tiempo real"

# Mostrar logs de bff_web
echo ""
echo "📋 Logs del bff_web (Ctrl+C para salir):"
docker logs -f bff-web-test