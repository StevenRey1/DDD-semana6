# Microservicio de Procesamiento de Pagos (Simplificado)

## Especificación Técnica Implementada

### Responsabilidades
- ✅ Procesar pagos solicitados basados en comandos
- ✅ Consultar estados de pago
- ✅ Publicar eventos de pago procesado

## API Endpoints

### Comando
**Nombre:** PagoCommand  
**Endpoint:** `POST /pagos`  
**Response:** HTTP 202 Accepted

**Request Structure:**
```json
{
  "comando": "Iniciar | Cancelar",  
  "idTransaction": "222e4567-e89b-12d3-a456-98546546544", // Opcional
  "data": {
    "idEvento": "uuid",
    "idSocio": "uuid", 
    "monto": 123.45,
    "fechaEvento": "2025-09-09T20:00:00Z"
  }
}
```

### Consulta
**Nombre:** ObtenerEstadoPagoQuery  
**Endpoint:** `GET /pagos/{idPago}`  
**Response:** HTTP 200

**Response Structure:**
```json
{
  "idTransaction": "222e4567-e89b-12d3-a456-98546546544",
  "idPago": "uuid",
  "idSocio": "uuid",
  "pago": 123.45,
  "estado_pago": "solicitado | completado | rechazado",
  "fechaPago": "2025-09-09T20:00:00Z"
}
```

## Eventos

### PagoProcesado
**Tópico Pulsar:** `eventos-pago`

```json
{
  "idTransaction": "222e4567-e89b-12d3-a456-98546546544",
  "idPago": "uuid",
  "idEvento": "uuid", 
  "idSocio": "uuid",
  "monto": 123.45,
  "estado_pago": "solicitado | completado | rechazado",
  "fechaPago": "2025-09-09T20:00:00Z"
}
```

## Suscripciones
- ✅ Escucha `PagoCommand` (tópico `comando-pago`)

## Arquitectura Simplificada

### Dominio
- **Entidad:** `Pago` - Agregado raíz limpio
- **Evento:** `PagoProcesado` - Único evento de dominio

### Aplicación  
- **Comando:** `PagoCommand` - Maneja Iniciar y Cancelar
- **Query:** `ObtenerEstadoPagoQuery` - Consulta estado por ID
- **Handlers:** CQRS con auto-registro

### Infraestructura
- **Repositorio:** PostgreSQL con outbox pattern
- **Messaging:** Pulsar (solo comando-pago y eventos-pago)
- **API:** FastAPI con endpoints REST

## Estructura de Archivos Limpia

```
src/pagos/
├── main.py                           # Punto de entrada
├── presentacion/api.py               # Endpoints REST
├── modulos/
│   ├── dominio/
│   │   ├── entidades.py             # Entidad Pago
│   │   └── eventos/pagos.py         # Evento PagoProcesado
│   ├── aplicacion/
│   │   ├── comandos/
│   │   │   ├── pago_command.py      # Comando unificado
│   │   │   └── pago_command_handler.py
│   │   └── queries/
│   │       ├── obtener_estado_pago.py
│   │       └── obtener_estado_pago_handler.py
│   └── infraestructura/
│       ├── repositorio_postgresql.py  # Persistencia
│       └── comando_pago_consumer.py   # Consumer único
├── schema/
│   ├── comandos_pagos.py            # Schema comando
│   └── eventos_pagos.py             # Schema evento
└── test/
    ├── test_api_pagos.py            # Tests API
    ├── test_consumer_comando.py     # Tests consumer
    ├── test_dominio_pagos.py        # Tests dominio
    ├── test_evento_pago_procesado.py # Tests eventos
    ├── test_integracion_pago_command.py # Tests integración
    └── test_outbox_publicacion.py   # Tests outbox
```

## Tópicos Pulsar

### Consumo
- `comando-pago` - Recibe comandos PagoCommand

### Publicación  
- `eventos-pago` - Publica eventos PagoProcesado

## Validación
```bash
python test_microservicio_completo.py
```

## Health Check
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "pagos"
}
```