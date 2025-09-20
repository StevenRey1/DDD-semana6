# 🧪 Setup de Prueba - BFF Web + Eventos

Este documento explica cómo configurar y probar el sistema de eventos del bff_web de manera autocontenida.

## 📋 Arquitectura

```
Usuario → UI (localhost:8081)
       ↓
bff_web (localhost:8000)
  ├── GraphQL API (/v1/graphql)
  ├── SSE Stream (/stream)
  └── Pulsar Consumer (eventos-tracking)

Pulsar (localhost:6650)
  ├── eventos-tracking (eventos de salida)
  └── comando-tracking (comandos de entrada)
```

## 🚀 Inicio Rápido

### 1. Levantar Servicios
```bash
# Levantar todos los servicios
docker-compose -f docker-compose.test.yml up -d

# Verificar que estén corriendo
docker ps
```

### 2. Configurar Tópicos
```bash
# Ejecutar script de configuración
chmod +x test-setup.sh
./test-setup.sh
```

Este script automáticamente:
- ✅ Crea los tópicos necesarios en Pulsar
- ✅ Muestra URLs de acceso
- ✅ Monitorea logs del bff_web

### 3. Probar el Sistema

#### 🌐 Interfaz Web
1. Abrir: `http://localhost:8081`
2. Llenar formulario de "Crear Evento"
3. Hacer clic en "Crear Evento"
4. Ver evento aparecer en tiempo real

#### 📊 GraphQL API
```bash
# Endpoint: http://localhost:8000/v1/graphql

# Mutation para crear evento
mutation {
  crear_evento(
    tipoEvento: "venta_creada"
    idReferido: "123e4567-e89b-12d3-a456-426614174004"
    idSocio: "123e4567-e89b-12d3-a456-426614174004"
    monto: 150.50
    estado_evento: "pendiente"
  ) {
    mensaje
    codigo
  }
}

# Query para consultar eventos
query {
  eventos_socio(id_socio: "123e4567-e89b-12d3-a456-426614174004") {
    idSocio
    eventos {
      idEvento
      tipo_evento
      idReferido
      monto
      estado_evento
      fechaEvento
    }
  }
}
```

#### 📡 SSE Stream
- URL: `http://localhost:8000/stream`
- Recibe eventos en tiempo real vía Server-Sent Events

## 🔧 Servicios Disponibles

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **UI** | http://localhost:8081 | Interfaz web para crear eventos |
| **BFF API** | http://localhost:8000 | API REST/GraphQL principal |
| **GraphQL** | http://localhost:8000/v1/graphql | Endpoint GraphQL |
| **SSE Stream** | http://localhost:8000/stream | Eventos en tiempo real |
| **Pulsar Admin** | http://localhost:8080 | Interfaz de administración de Pulsar |

## 📝 Flujo de Eventos

1. **Usuario** crea evento vía formulario web
2. **JavaScript** envía mutation GraphQL al bff_web
3. **bff_web** publica comando a `comando-tracking`
4. **bff_web** consume respuesta de `eventos-tracking`
5. **bff_web** transmite evento vía SSE
6. **UI** muestra evento en tiempo real

## 🛠️ Comandos Útiles

```bash
# Ver logs
docker logs -f bff-web-test
docker logs -f pulsar-test

# Reiniciar servicios
docker-compose -f docker-compose.test.yml restart

# Detener todo
docker-compose -f docker-compose.test.yml down

# Limpiar datos
docker volume rm $(docker volume ls -q)
```

## 🐛 Solución de Problemas

### Servicio no inicia
```bash
# Verificar estado
docker ps

# Ver logs específicos
docker logs bff-web-test
docker logs pulsar-test
```

### Error de conexión
```bash
# Verificar que servicios estén en la misma red
docker network ls
docker network inspect alpespartners-shared
```

### Tópicos no existen
```bash
# Crear tópicos manualmente
docker exec pulsar-test bin/pulsar-admin topics create persistent://public/default/eventos-tracking
docker exec pulsar-test bin/pulsar-admin topics create persistent://public/default/comando-tracking
```

## 📊 Monitoreo

### Logs del bff_web
```bash
docker logs -f bff-web-test
```

### Estado de Pulsar
```bash
# Ver tópicos
curl http://localhost:8080/admin/v2/persistent/public/default

# Ver estadísticas
curl http://localhost:8080/admin/v2/persistent/public/default/eventos-tracking/stats
```

## 🎯 Próximos Pasos

Una vez probado este setup básico, puedes:

1. **Agregar eventosMS** real para procesar comandos
2. **Implementar autenticación** en la API
3. **Agregar más tipos de eventos**
4. **Implementar persistencia** de eventos
5. **Agregar métricas y monitoreo**

¡El sistema está listo para pruebas! 🚀