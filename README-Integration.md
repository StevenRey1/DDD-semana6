# Pruebas de Integración - Referidos & Notificaciones

Este docker-compose permite probar la integración completa entre los microservicios de Referidos y Notificaciones con infraestructura compartida.

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Referidos    │    │ Notificaciones  │    │   PostgreSQL    │
│   (Puerto 5001) │    │  (Puerto 8002)  │    │   (Puerto 5434) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Apache Pulsar  │
                    │  (Puerto 6653)  │
                    └─────────────────┘
```

## 🚀 Inicio Rápido

### Windows (PowerShell)
```powershell
# Levantar toda la infraestructura
.\test-integration.ps1 up

# Ejecutar prueba completa
.\test-integration.ps1 test

# Ver logs en tiempo real
.\test-integration.ps1 logs

# Bajar todo
.\test-integration.ps1 down
```

### Linux/Mac (Bash)
```bash
# Hacer ejecutable el script
chmod +x test-integration.sh

# Levantar toda la infraestructura
./test-integration.sh up

# Ejecutar prueba completa
./test-integration.sh test

# Ver logs en tiempo real
./test-integration.sh logs

# Bajar todo
./test-integration.sh down
```

## 📊 Puertos Expuestos

| Servicio | Puerto | Descripción |
|----------|---------|-------------|
| Referidos | 5001 | API REST del microservicio |
| Notificaciones | 8002 | API REST del microservicio |
| PostgreSQL | 5434 | Base de datos compartida |
| Pulsar Broker | 6653 | Message broker |
| Pulsar Admin | 8083 | API de administración |
| Pulsar Web UI | 8084 | Interfaz web |
| Pulsar Manager | 9529 | Herramienta de gestión |

## 🧪 Flujo de Prueba

1. **Envío de Evento**: Se envía un evento `EventoRegistrado` al topic `eventos-tracking`
2. **Procesamiento en Referidos**: 
   - Consume el evento
   - Crea un referido automáticamente
   - Guarda en la base de datos
   - Publica `VentaReferidaConfirmada` al topic `eventos-referido-confirmado`
3. **Procesamiento en Notificaciones**:
   - Consume el evento de confirmación
   - Crea una notificación
   - Guarda en la base de datos

## 🔍 Verificación Manual

### Health Checks
```bash
# Referidos
curl http://localhost:5001/health

# Notificaciones  
curl http://localhost:8002/health
```

### Pulsar Admin
```bash
# Listar topics
curl http://localhost:8083/admin/v2/topics/public/default

# Ver stats de un topic
curl http://localhost:8083/admin/v2/topics/public/default/eventos-tracking/stats
```

### Base de Datos
```bash
# Conectar a PostgreSQL
docker exec -it postgres-shared psql -U postgres -d alpespartners

# Ver tablas
\dt

# Ver referidos
SELECT * FROM referidos;

# Ver notificaciones
SELECT * FROM notificaciones;
```

## 🔧 Comandos Útiles

```bash
# Ver logs de un servicio específico
docker logs referidos-shared -f
docker logs notificaciones-shared -f
docker logs pulsar-shared -f

# Ejecutar comando en un contenedor
docker exec -it referidos-shared bash
docker exec -it notificaciones-shared bash

# Reiniciar un servicio específico
docker-compose -f docker-compose.integration.yml restart referidos
docker-compose -f docker-compose.integration.yml restart notificaciones

# Ver el estado de todos los contenedores
docker-compose -f docker-compose.integration.yml ps
```

## 🐛 Troubleshooting

### Servicios no arrancan
```bash
# Ver logs de arranque
docker-compose -f docker-compose.integration.yml logs

# Verificar que no hay conflictos de puertos
netstat -an | grep "5001\|8002\|5434\|6653"
```

### Eventos no se procesan
```bash
# Verificar conexiones Pulsar
curl http://localhost:8083/admin/v2/topics/public/default/eventos-tracking/stats

# Ver subscriptions activas
curl http://localhost:8083/admin/v2/topics/public/default/eventos-tracking/subscriptions
```

### Base de datos no conecta
```bash
# Verificar PostgreSQL
docker exec -it postgres-shared pg_isready -U postgres

# Ver logs de PostgreSQL
docker logs postgres-shared
```

## 🧹 Limpieza

```bash
# Bajar todo y limpiar volúmenes
.\test-integration.ps1 clean

# O manualmente
docker-compose -f docker-compose.integration.yml down -v
docker system prune -f
```

## 📋 Checklist de Validación

- [ ] Referidos arranca correctamente
- [ ] Notificaciones arranca correctamente  
- [ ] PostgreSQL acepta conexiones
- [ ] Pulsar broker está disponible
- [ ] Health checks responden OK
- [ ] Script de prueba ejecuta sin errores
- [ ] Referidos procesa eventos de tracking
- [ ] Referidos guarda en BD y publica confirmación
- [ ] Notificaciones consume eventos de confirmación
- [ ] Notificaciones crea y guarda notificaciones
- [ ] Logs muestran flujo completo sin errores