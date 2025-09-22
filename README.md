# Pruebas de Integración - Microservicios DDD
Este documento describe cómo probar la integración de los microservicios del proyecto, la estructura, el despliegue y cómo se cumplen los escenarios de calidad arquitecturales.

---

## 🏗️ Estructura del Proyecto

- **Microservicios:** Referidos, Notificaciones, Pagos, Eventos, Pulsar Manager
- **Bases de datos:** Cada microservicio tiene su propia instancia de PostgreSQL
- **Mensajería:** Apache Pulsar para comunicación asíncrona
- **Orquestación:** Docker Compose para levantar toda la infraestructura

```




                ┌───────────────────────────────┐
                │            BFF (8000)         │
                │  (Inicia Saga: CrearEvento)   │
                └───────────────┬───────────────┘
                                │  Evento inicial
                                ▼
Referidos (8004)   Pagos (8080)   Notificaciones (8002)   Eventos (8003)
      │                │                │                    │
      │                │                │   (Coordinador Saga + Saga Log)
      │                │                │            │
      └──────┬─────────┴───────┬────────┴──────┬─────┘
             │                 │               │
             │        Apache Pulsar (6653 / 8083)
             │        Topics: 
             │          - eventos-* (CrearEvento, EventoRegistrado)
             │          - referido-* (ReferidoProcesado)
             │          - pagos-* (PagoProcesado)
             │          - notificaciones-* (opcional)
             ▼
        Coordinador Saga
        (Orquestación pasos,
         publica comandos,
         persiste trazas en saga_log)
        
        saga_log (tabla PostgreSQL)
        Campos: id, id_transaction, tipo, nombre, paso, estado, timestamp
```

---

## 🚀 Despliegue de Servicios

Para levantar todos los servicios:
```bash
docker-compose -f docker-compose.yml up -d --build
```

## ️🚀 Recomendaciones de Arranque (Orden Sugerido)

Para evitar errores de dependencias (schemas Avro no disponibles, consumidores sin broker, etc.) sigue este orden:

1. Construir y levantar Apache Pulsar primero  
   docker compose up -d --build pulsar  
   (Espera a que la consola/web esté accesible en http://localhost:8083 si la tienes habilitada)

2. Crear / registrar (si aplica) los schemas Avro necesarios (si usas script: ./scripts/upload_schemas.sh)

3. Levantar base(s) de datos (PostgreSQL)  
   docker compose up -d eventos-db

4. Levantar los microservicios de dominio (sin BFF todavía)  
   docker compose up -d --build eventos referidos pagos notificaciones

5. Verificar health de cada microservicio  
   curl http://localhost:8004/health  (Eventos)  
   curl http://localhost:8001/health  (Referidos)  
   curl http://localhost:8002/health  (Pagos)  
   curl http://localhost:8003/health  (Notificaciones)  

6. (Opcional) Confirmar consumidores conectados en logs de “eventos”

7. Recién después levantar el BFF  
   docker compose up -d --build bff

8. Finalmente levantar la UI (si existe app frontend)  
   docker compose up -d --build ui

Si algo falla (por ejemplo “Working outside of application context” o schema no encontrado), detén solo el servicio afectado y vuelve a levantarlo; no reinicies Pulsar salvo que cambies schemas.


Para bajar y limpiar:
```bash
docker-compose -f docker-compose.yml down --volumes --remove-orphans
```

---

### Puertos Estándar (ajusta si tu compose difiere)

| Componente        | Puerto | Descripción                                |
|-------------------|--------|--------------------------------------------|
| UI (frontend)     | 8081   | Aplicación web (ejemplo Vite)              |
| BFF               | 8000   | Backend For Frontend / API Gateway         |
| Eventos           | 8003   | Servicio de orquestación + Saga Log        |
| Referidos         | 8004   | Microservicio referidos                    |
| Pagos             | 8080   | Microservicio pagos                        |
| Notificaciones    | 8002   | Microservicio notificaciones (si aplica)   |
| PostgreSQL eventos| 5435   | Base de datos (alpespartners)              |
| Pulsar Broker     | 6653   | (o 6650) Puerto binario cliente            |
| Pulsar Web / UI   | 8083   | Consola / Admin (o 8080 según imagen)      |

Nota: Verifica en docker-compose.yml los puertos reales; si tu UI usa otro (ej: 4200 Angular), actualiza la tabla.
---

## 🧪 Flujo de Prueba

1. **Envío de Evento:** Se envía un evento a Pulsar.
2. **Procesamiento:** Cada microservicio consume, procesa y publica eventos según su lógica.
3. **Persistencia:** Cada servicio guarda sus datos en su propia base de datos.

---

## 📋 Escenarios de Calidad y Cumplimiento

### Escalabilidad

**Escenario #2 — Manejo de crecimiento sostenido de clientes e influencers (2 años)**

- **Fuente:** Nuevos clientes, marcas, usuarios e influencers
- **Estímulo:** Aumento gradual y constante en la base de usuarios, marcas y concurrencia de nuevos clientes
- **Ambiente:** Operación normal a lo largo del tiempo
- **Artefacto:** Sistema completo, en particular los microservicios de Onboarding, Afiliados, Influencers y Tracking de eventos
- **Respuesta esperada:** El sistema debe responder correctamente ante el incremento de carga de uso
- **Medida de la respuesta:** Hasta 160,000 transacciones por minuto después de 2 años

**¿Cómo lo resolvemos en este proyecto?**
- **Microservicios desacoplados:** Cada dominio relevante (referidos, pagos, notificaciones, eventos) es un microservicio independiente, permitiendo escalar horizontalmente solo los componentes que lo requieran. Por ejemplo, si el tracking de eventos crece más rápido, solo ese servicio se replica.
- **Bases de datos independientes:** Cada microservicio tiene su propia base de datos, evitando cuellos de botella y permitiendo optimización específica por servicio.
- **Mensajería asíncrona (Pulsar):** El uso de Apache Pulsar desacopla la comunicación, permitiendo que los servicios procesen eventos a su propio ritmo y soporten picos de carga sin perder mensajes.
- **CQRS:** En servicios críticos, se separan los modelos de lectura y escritura, optimizando cada uno para su carga específica. Esto permite que consultas masivas no ralenticen las escrituras intensivas.
- **Monitoreo y healthchecks:** Cada servicio expone endpoints de salud y logs, permitiendo detectar cuellos de botella y escalar proactivamente.
- **Trade-offs y riesgos:** Se asume mayor complejidad operativa y posible latencia interservicios, mitigada con colas y observabilidad. El desacoplamiento permite que el sistema crezca de forma sostenida y controlada, pero requiere una estrategia de monitoreo y escalado automatizado.

### Modificabilidad

**Escenario #5 — Actualizar el framework de la capa API**

- **Objetivo:** Reemplazar el framework web de un microservicio para mejorar rendimiento
- **Fuente:** Equipo de Desarrollo / Arquitecto de Software
- **Estímulo:** Necesidad de mejorar rendimiento y concurrencia del servicio
- **Ambiente:** Desarrollo
- **Artefacto:** API del servicio de Pagos
- **Respuesta esperada:** Se añade FastAPI como nueva dependencia y se elimina Flask; se reescriben los módulos de rutas (de @app.route('/...') a @router.post('/...'), etc.)
- **Medida de la respuesta:** 0% de cambios en Dominio (entidades y reglas de negocio), Aplicación (casos de uso) y adaptadores de salida de Infraestructura (repositorios, publicadores de eventos)

**¿Cómo lo resolvemos en este proyecto?**
- **Arquitectura hexagonal/limpia:** El código está organizado en capas (Presentación/API, Aplicación, Dominio, Infraestructura). Los adaptadores de entrada (API) y salida (BD/eventos) están desacoplados de la lógica de negocio.
- **Separación estricta:** Cambiar el framework web solo afecta la capa de Presentación. El Dominio y la Aplicación no requieren cambios, garantizando modificabilidad y bajo esfuerzo de migración.
- **Ejemplo real:** El servicio de Pagos puede migrar de Flask a FastAPI sin tocar entidades, casos de uso ni repositorios, cumpliendo la medida de respuesta. Esto se logra porque la lógica de negocio y la persistencia están completamente desacopladas de la API.
- **Trade-offs y riesgos:** Si la lógica de negocio estuviera acoplada a la API, la migración sería costosa. Por eso se refuerza la separación desde el diseño y se revisan los PRs para evitar acoplamientos indebidos.

### Disponibilidad / Resiliencia

**Escenario #7 — Falla de microservicio crítico**

- **Fuente:** Sistema de orquestación (Kubernetes, ECS)
- **Estímulo:** Caída inesperada del microservicio de Pagos
- **Ambiente:** Producción en modo normal (campañas activas)
- **Artefacto:** Servicio de Pagos (pod/contenedor) y Event Bus
- **Respuesta esperada:**
   - Los eventos pendientes se envían al tópico de eventos-referido-confirmado.
   - Se realizan reintentos automáticos hasta su reproceso exitoso.
- **Medida de la respuesta:**
   - SLA ≥ 99.95% (tiempo máximo de caída mensual ≤ 22 min)
   - Pérdida de eventos = 0%
   - Reprocesamiento < 5 min

**¿Cómo lo resolvemos en este proyecto?**
- **Microservicios aislados:** Cada servicio corre en su propio contenedor, evitando que una falla se propague a otros. El orquestador (Docker Compose, Kubernetes) puede reiniciar servicios caídos sin afectar el resto.
- **Event Bus + DLQ:** Apache Pulsar gestiona los eventos y cuenta con Dead Letter Queue para reintentos automáticos. Si Pagos falla, los eventos se almacenan y se reprocesan cuando el servicio vuelve a estar disponible, garantizando que no se pierdan transacciones.
- **Healthchecks y monitoreo:** Los endpoints de salud permiten al orquestador detectar fallos y reiniciar servicios automáticamente. Los logs y métricas permiten auditar la recuperación y el reprocesamiento.
- **Trade-offs y riesgos:** Se incrementa la complejidad de monitoreo y orquestación, pero se garantiza la resiliencia y la continuidad operativa. El sistema sacrifica inmediatez en favor de robustez y experiencia de usuario.

---

## 🔍 Validación y Monitoreo

- **Health Checks:** Cada microservicio expone `/health`
- **Logs:** Revisión de logs en tiempo real por servicio
- **Pulsar Admin:** Verificación de topics y eventos procesados
- **Base de datos:** Consulta directa a cada instancia PostgreSQL

---

## 🐛 Troubleshooting

- **Conflictos de puertos:** Verifica con `netstat` y ajusta puertos en `docker-compose.integration.yml`
- **Eventos no procesados:** Revisa subscriptions y DLQ en Pulsar
- **Servicios caídos:** Reinicia con Docker Compose y revisa healthchecks

---

## 🧹 Limpieza

```bash
docker-compose -f docker-compose.yml down --volumes --remove-orphans
docker system prune -f
```

---

## ✅ Checklist de Calidad

- [x] Microservicios desacoplados y escalables
- [x] Cada servicio con su propia base de datos
- [x] Healthchecks y monitoreo activo
- [x] CQRS implementado en servicios críticos
- [x] Resiliencia ante fallos con Event Bus y DLQ
- [x] Modificabilidad garantizada por arquitectura hexagonal



## Descripción de actividades realizada por cada miembro

| No | Actividad                  | Realizó                        |
|----|-----------------------------|--------------------------------|
| 1  | Microservicio Pagos         | Nicolas Valderrama             |
| 2  | Microservicio Referidos     | Jose Hernandez                 |
| 3  | Microservicio Notificaciones| Jesús Rey                      |
| 4  | Microservicio Eventos       | Fabiani Lozano                 |
| 5  | Docker Compose              | Pair programming               |
| 6  | Implementación Bff          | Jesús Rey                      |
| 7  | Implementación saga Log     | Pair programming               |
| 8  | Implementación Saga         | Fabiani Lozano                 |
| 8  | Implementación UI           | Pair programming               |
| 9  | Readme                      | Nicolas Valderrama - Jesús Rey |






