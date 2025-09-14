# Pruebas de Integración - Microservicios DDD
Este documento describe cómo probar la integración de los microservicios del proyecto, la estructura, el despliegue y cómo se cumplen los escenarios de calidad arquitecturales.

---

## 🏗️ Estructura del Proyecto

- **Microservicios:** Referidos, Notificaciones, Pagos, Eventos, Pulsar Manager
- **Bases de datos:** Cada microservicio tiene su propia instancia de PostgreSQL
- **Mensajería:** Apache Pulsar para comunicación asíncrona
- **Orquestación:** Docker Compose para levantar toda la infraestructura

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  Referidos  │   │ Pagos       │   │ Notificaciones │ │ Eventos    │
│  (8003)     │   │ (8080)      │   │ (8002)         │ │ (8003)     │
└─────┬───────┘   └─────┬───────┘   └─────┬──────────┘ └─────┬──────┘
         │                │                 │                   │
         └────────────────┴─────────────────┴──────────────────┘
                                    │
                     ┌─────────────────┐
                     │  Apache Pulsar  │
                     │  (6653, 8083)   │
                     └─────────────────┘
```

---

## 🚀 Despliegue de Servicios

### Linux/Mac
```bash
chmod +x test-integration.sh
./test-integration.sh up
```

### Windows
```powershell
.\test-integration.ps1 up
```

Para bajar y limpiar:
```bash
docker-compose -f docker-compose.integration.yml down --volumes --remove-orphans
```

---

## 📊 Puertos Expuestos

| Servicio         | Puerto | Descripción                  |
|------------------|--------|------------------------------|
| Referidos        | 8004   | API REST                     |
| Pagos            | 8080   | API REST                     |
| Notificaciones   | 8002   | API REST                     |
| Eventos          | 8003   | API REST                     |
| PostgreSQL (x4)  | 5440+  | BD por microservicio         |
| Pulsar Broker    | 6653   | Mensajería                   |
| Pulsar Admin     | 8083   | API de administración        |
| Pulsar Web UI    | 8084   | Interfaz web                 |
| Pulsar Manager   | 9529   | Herramienta de gestión       |

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
   - El API Gateway enruta peticiones a instancias saludables.
   - Los eventos pendientes se envían a la DLQ (cola de reintentos).
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
docker-compose -f docker-compose.integration.yml down --volumes --remove-orphans
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
| 6  | Readme                      | Nicolas Valderrama - Jesús Rey |
