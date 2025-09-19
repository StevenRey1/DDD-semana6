# Guía de Validación del Servicio de Pagos

Este documento describe cómo validar y probar el servicio de Pagos containerizado con todas las mejoras implementadas.

## Estructura de Testing Implementada

### 1. Tests de Integración API
**Archivo**: `test/test_integracion_pago_command.py`
- ✅ Validación completa de endpoints según especificación de contrato
- ✅ Tests de comando `Iniciar` y `Cancelar` 
- ✅ Tests de consulta `ObtenerEstadoPagoQuery`
- ✅ Validación de estructura de respuesta
- ✅ Tests de flujo completo (crear → consultar → cancelar)
- ✅ Tests de validación de campos requeridos

### 2. Tests de Consumer Pulsar
**Archivo**: `test/test_consumer_comando.py`
- ✅ Validación de consumer `comando-pago`
- ✅ Tests de envío de comandos via Pulsar
- ✅ Tests de comandos secuenciales
- ✅ Validación de schema de comandos
- ✅ Tests de integración comando → evento

### 3. Tests de Eventos
**Archivo**: `test/test_evento_pago_procesado.py`
- ✅ Validación de eventos `PagoProcesado`
- ✅ Tests de estructura de eventos según schema Avro
- ✅ Tests de publicación en topic `eventos-pago`
- ✅ Validación de formato de fechas
- ✅ Tests de eventos múltiples transacciones

### 4. Script de Validación Completa
**Archivo**: `script_validacion.py`
- ✅ Validación automática de estructura del proyecto
- ✅ Verificación de disponibilidad de servicios
- ✅ Tests de endpoints críticos
- ✅ Validación de logs de errores
- ✅ Reporte completo de resultados

### 5. Script de Comando Docker
**Archivo**: `probar_servicio.sh`
- ✅ Comandos para levantar/parar servicios
- ✅ Espera automática de disponibilidad de servicios
- ✅ Tests básicos integrados
- ✅ Visualización de logs y estado
- ✅ Limpieza completa de recursos

## Comandos de Validación

### Opción 1: Script Automático (Recomendado)
```bash
cd src/pagos

# Levantar servicios
./probar_servicio.sh start

# Ejecutar validación completa
./probar_servicio.sh test

# Ver estado de servicios
./probar_servicio.sh status

# Ver logs
./probar_servicio.sh logs

# Parar servicios
./probar_servicio.sh stop
```

### Opción 2: Manual Docker Compose
```bash
cd src/pagos

# Levantar servicios
docker-compose -f docker-compose.dev.yml up -d

# Ejecutar validación
python script_validacion.py

# Ejecutar tests específicos
python -m pytest test/test_integracion_pago_command.py -v
python -m pytest test/test_consumer_comando.py -v
python -m pytest test/test_evento_pago_procesado.py -v
```

### Opción 3: Tests Individuales
```bash
# Test directo de API
python test/test_integracion_pago_command.py

# Test directo de consumer
python test/test_consumer_comando.py

# Test directo de eventos
python test/test_evento_pago_procesado.py
```

## Servicios del Contenedor

El `docker-compose.dev.yml` levanta:

1. **postgres-pagos** (Puerto 5433)
   - Base de datos PostgreSQL para persistencia
   - Esquema inicializado automáticamente

2. **pulsar** (Puerto 6650)
   - Apache Pulsar para mensajería
   - Topics: `comando-pago`, `eventos-pago`

3. **api** (Puerto 8090) 
   - API FastAPI con endpoints según especificación
   - CQRS handlers cargados automáticamente
   - Health check en `/health`

4. **worker**
   - Consumer de `comando-pago`
   - Procesa comandos y publica eventos
   - Usa nuevo `comando_pago_consumer.py`

## Contratos Validados

### API Endpoints
- `POST /pagos` - Acepta `PagoCommand` con `comando: "Iniciar|Cancelar"`
- `GET /pagos/{idPago}` - Retorna estado completo del pago
- `GET /health` - Health check del servicio

### Schemas Avro
- **PagoCommandMessage**: Schema para topic `comando-pago`
- **PagoProcesado**: Schema para topic `eventos-pago`

### Flujo Completo Validado
1. Comando → API → CQRS Handler → Base de Datos → Evento
2. Comando → Pulsar → Consumer → CQRS Handler → Base de Datos → Evento
3. Query → API → CQRS Handler → Base de Datos → Respuesta

## Métricas de Validación

El script de validación verifica:
- ✅ Estructura del proyecto limpia (sin archivos obsoletos)
- ✅ Servicios disponibles y funcionando
- ✅ API endpoints respondem correctamente
- ✅ Comandos CQRS procesados exitosamente
- ✅ Eventos publicados con estructura correcta
- ✅ Base de datos persistiendo datos
- ✅ Logs sin errores críticos

## Troubleshooting

### Si falla la validación:
1. Verificar logs: `./probar_servicio.sh logs`
2. Verificar estado: `./probar_servicio.sh status`
3. Reiniciar servicios: `./probar_servicio.sh restart`

### Si hay problemas de permisos:
```bash
chmod +x probar_servicio.sh
chmod +x script_validacion.py
```

### Si Pulsar no se conecta:
```bash
# Dar más tiempo para que Pulsar esté listo
sleep 30
./probar_servicio.sh test
```

## Resultado Esperado

Al ejecutar `./probar_servicio.sh test` debería mostrar:
```
🎉 SERVICIO COMPLETAMENTE VALIDADO
Total de validaciones: 7
Exitosas: 7
Fallidas: 0
```

Este indica que el servicio está funcionando correctamente según las especificaciones de contrato implementadas.