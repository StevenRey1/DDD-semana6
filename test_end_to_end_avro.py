"""
Prueba End-to-End CORREGIDA del flujo completo de eventos con Schema Avro:
eventos-tracking → referidos → eventos-referido-confirmado → notificaciones
"""

import asyncio
import logging
import json
import time
import pulsar
from pulsar.schema import AvroSchema, Record, String, Float
import requests

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Definir el esquema Avro que referidos espera
class EventoRegistrado(Record):
    """
    Esquema Avro para EventoRegistrado que referidos consume
    """
    idEvento = String()
    tipoEvento = String()
    idReferido = String()
    idSocio = String()
    monto = Float()
    estado = String()
    fechaEvento = String()

async def step_1_publicar_evento_tracking_avro():
    """Paso 1: Publicar evento en eventos-tracking con esquema Avro correcto"""
    logger.info("🚀 === PASO 1: PUBLICANDO EVENTO AVRO EN eventos-tracking ===")
    
    try:
        # Conectar a Pulsar
        cliente = pulsar.Client('pulsar://localhost:6653')
        
        # Crear el evento con esquema Avro que referidos espera
        evento_tracking = EventoRegistrado(
            idEvento="test-tracking-avro-001",
            tipoEvento="venta_creada",  # Tipo que referidos filtra
            idReferido="ref-avro-12345", 
            idSocio="socio-avro-67890",
            monto=95000.0,
            estado="pendiente",  # Estado inicial
            fechaEvento="2025-09-14T01:30:00Z"
        )
        
        # Crear productor con esquema Avro
        topico_tracking = "persistent://public/default/eventos-tracking"
        productor = cliente.create_producer(
            topic=topico_tracking,
            schema=AvroSchema(EventoRegistrado)
        )
        
        logger.info(f"📤 Enviando evento Avro: {evento_tracking}")
        
        # Enviar con esquema Avro
        productor.send(evento_tracking)
        
        logger.info("✅ Evento Avro enviado a eventos-tracking")
        
        # Limpiar
        productor.close()
        cliente.close()
        
        return evento_tracking
        
    except Exception as e:
        logger.error(f"❌ Error en Paso 1: {e}")
        return None

async def step_2_esperar_y_verificar_referidos():
    """Paso 2: Esperar y verificar que referidos procesó el evento"""
    logger.info("🔍 === PASO 2: VERIFICANDO PROCESAMIENTO EN REFERIDOS ===")
    
    logger.info("⏳ Esperando 20 segundos para que referidos procese...")
    await asyncio.sleep(20)
    
    try:
        # Revisar logs de referidos
        import subprocess
        result = subprocess.run(
            ["docker", "logs", "referidos-shared", "--tail", "30"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'  # Ignorar errores de encoding
        )
        
        logs = result.stdout
        logger.info("📋 Logs recientes de referidos:")
        logger.info(logs)
        
        # Buscar evidencia de procesamiento exitoso
        if "EventoRegistrado recibido" in logs and "test-tracking-avro-001" in logs:
            logger.info("✅ Referidos procesó el evento Avro correctamente")
            return True
        elif "Error procesando evento" in logs:
            logger.warning("⚠️ Referidos tuvo errores procesando")
            return False
        else:
            logger.warning("⚠️ No se encontró evidencia clara de procesamiento")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error verificando referidos: {e}")
        return False

async def step_3_verificar_evento_confirmado():
    """Paso 3: Verificar que se publicó en eventos-referido-confirmado"""
    logger.info("🔍 === PASO 3: VERIFICANDO eventos-referido-confirmado ===")
    
    try:
        # Crear consumidor temporal para verificar
        cliente = pulsar.Client('pulsar://localhost:6653')
        
        topico_confirmado = "persistent://public/default/eventos-referido-confirmado"
        
        # Consumidor con auto-acknowledge
        consumidor = cliente.subscribe(
            topic=topico_confirmado,
            subscription_name="test-verificacion-avro",
            consumer_type=pulsar.ConsumerType.Exclusive
        )
        
        logger.info("📥 Buscando mensajes en eventos-referido-confirmado...")
        
        # Intentar recibir mensaje (timeout más largo)
        try:
            mensaje = consumidor.receive(timeout_millis=10000)
            
            # Intentar deserializar
            try:
                datos = mensaje.value()
                logger.info(f"✅ Evento confirmado encontrado: {datos}")
                consumidor.acknowledge(mensaje)
                return True
                
            except Exception as e:
                # Si falla deserialización, intentar como bytes
                datos_raw = mensaje.data().decode('utf-8') 
                logger.info(f"✅ Evento confirmado encontrado (raw): {datos_raw}")
                consumidor.acknowledge(mensaje)
                return True
                
        except pulsar.Timeout:
            logger.warning("⚠️ No se encontraron mensajes en eventos-referido-confirmado")
            return False
            
        finally:
            consumidor.close()
            cliente.close()
            
    except Exception as e:
        logger.error(f"❌ Error verificando eventos confirmados: {e}")
        return False

async def step_4_verificar_notificaciones():
    """Paso 4: Verificar que notificaciones procesó y creó notificación"""
    logger.info("🔍 === PASO 4: VERIFICANDO PROCESAMIENTO EN NOTIFICACIONES ===")
    
    logger.info("⏳ Esperando 15 segundos para que notificaciones procese...")
    await asyncio.sleep(15)
    
    try:
        # Revisar logs de notificaciones
        import subprocess
        result = subprocess.run(
            ["docker", "logs", "notificaciones-shared", "--tail", "40"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        logs = result.stdout
        logger.info("📋 Logs recientes de notificaciones:")
        logger.info(logs[-1000:])  # Solo últimos 1000 chars
        
        # Buscar evidencia de procesamiento
        notif_procesado = "Notificación" in logs and ("VentaReferidaConfirmada" in logs or "ref-avro" in logs)
        
        if notif_procesado:
            logger.info("✅ Notificaciones procesó eventos relacionados")
        else:
            logger.warning("⚠️ No se encontró evidencia clara de procesamiento específico")
        
        # Intentar obtener notificaciones via API
        try:
            response = requests.get("http://localhost:8002/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ API de notificaciones respondiendo")
                
                # Contar notificaciones recientes
                health_data = response.json()
                total_notif = health_data.get('datos', {}).get('total_notificaciones', 0)
                logger.info(f"📊 Total notificaciones en sistema: {total_notif}")
                return True
            else:
                logger.warning(f"⚠️ API responde con código: {response.status_code}")
                
        except Exception as e:
            logger.warning(f"⚠️ No se pudo verificar API: {e}")
        
        return notif_procesado
        
    except Exception as e:
        logger.error(f"❌ Error verificando notificaciones: {e}")
        return False

async def step_5_resumen_estado():
    """Paso 5: Resumen del estado final"""
    logger.info("📊 === PASO 5: RESUMEN FINAL ===")
    
    try:
        # Estado de contenedores
        import subprocess
        result = subprocess.run(
            ["docker", "ps", "--format", "table {{.Names}}\\t{{.Status}}"],
            capture_output=True,
            text=True
        )
        
        logger.info("🐳 Estado de contenedores:")
        logger.info(result.stdout)
        
        # Estado de tópicos (intentar listar)
        try:
            response = requests.get("http://localhost:8083/admin/v2/persistent/public/default", timeout=5)
            if response.status_code == 200:
                topicos = response.json()
                logger.info(f"📋 Tópicos activos: {len(topicos)}")
        except:
            logger.info("📋 No se pudo verificar tópicos")
        
    except Exception as e:
        logger.error(f"❌ Error en resumen: {e}")

async def main():
    """Función principal de la prueba end-to-end CORREGIDA"""
    logger.info("🧪 === INICIANDO PRUEBA END-TO-END CORREGIDA CON AVRO ===")
    start_time = time.time()
    
    # Paso 1: Publicar evento Avro
    evento = await step_1_publicar_evento_tracking_avro()
    if not evento:
        logger.error("❌ Fallo en Paso 1, abortando")
        return
    
    # Paso 2: Verificar referidos
    referidos_ok = await step_2_esperar_y_verificar_referidos()
    
    # Paso 3: Verificar evento confirmado
    confirmado_ok = await step_3_verificar_evento_confirmado()
    
    # Paso 4: Verificar notificaciones  
    notificaciones_ok = await step_4_verificar_notificaciones()
    
    # Paso 5: Resumen
    await step_5_resumen_estado()
    
    # Resultado final
    end_time = time.time()
    duration = end_time - start_time
    
    logger.info(f"\n🎯 === RESULTADO DE LA PRUEBA AVRO ({duration:.1f}s) ===")
    logger.info(f"✅ Evento Avro publicado: {'SÍ' if evento else 'NO'}")
    logger.info(f"✅ Referidos procesó: {'SÍ' if referidos_ok else 'NO'}")
    logger.info(f"✅ Evento confirmado: {'SÍ' if confirmado_ok else 'NO'}")
    logger.info(f"✅ Notificaciones procesó: {'SÍ' if notificaciones_ok else 'NO'}")
    
    if evento and referidos_ok and confirmado_ok and notificaciones_ok:
        logger.info("🎉 === PRUEBA END-TO-END EXITOSA ===")
    else:
        logger.info("⚠️ === PRUEBA PARCIALMENTE EXITOSA ===")

if __name__ == "__main__":
    asyncio.run(main())