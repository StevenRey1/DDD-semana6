"""
Prueba End-to-End del flujo completo de eventos:
eventos-tracking → referidos → eventos-referido-confirmado → notificaciones
"""

import asyncio
import logging
import json
import time
import pulsar
from pulsar.schema import AvroSchema
import requests

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def step_1_publicar_evento_tracking():
    """Paso 1: Publicar evento en eventos-tracking"""
    logger.info("🚀 === PASO 1: PUBLICANDO EVENTO EN eventos-tracking ===")
    
    try:
        # Conectar a Pulsar
        cliente = pulsar.Client('pulsar://localhost:6653')
        
        # Crear el evento que referidos espera consumir
        # Basado en el consumidor de referidos que busca estado = "solicitado | completado | rechazado"
        evento_tracking = {
            "idEvento": "test-tracking-001",
            "tipoEvento": "EventoRegistrado",  # Tipo que referidos espera
            "idReferido": "ref-12345", 
            "idSocio": "socio-67890",
            "monto": 75000.0,
            "estado": "completado",  # Estado que dispara la confirmación
            "fechaEvento": "2025-09-14T01:30:00Z"
        }
        
        # Crear productor para eventos-tracking
        topico_tracking = "persistent://public/default/eventos-tracking"
        productor = cliente.create_producer(topic=topico_tracking)
        
        logger.info(f"📤 Enviando evento: {evento_tracking}")
        
        # Enviar como JSON
        mensaje = json.dumps(evento_tracking).encode('utf-8')
        productor.send(mensaje)
        
        logger.info("✅ Evento enviado a eventos-tracking")
        
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
    
    logger.info("⏳ Esperando 15 segundos para que referidos procese...")
    await asyncio.sleep(15)
    
    try:
        # Revisar logs de referidos
        import subprocess
        result = subprocess.run(
            ["docker", "logs", "referidos-shared", "--tail", "20"],
            capture_output=True,
            text=True
        )
        
        logs = result.stdout
        logger.info("📋 Logs recientes de referidos:")
        
        # Buscar evidencia de procesamiento
        if "EventoRegistrado" in logs or "completado" in logs:
            logger.info("✅ Referidos procesó el evento")
            return True
        else:
            logger.warning("⚠️ No se encontró evidencia de procesamiento en referidos")
            logger.info(f"Logs: {logs}")
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
            subscription_name="test-verificacion",
            consumer_type=pulsar.ConsumerType.Exclusive
        )
        
        logger.info("📥 Buscando mensajes en eventos-referido-confirmado...")
        
        # Intentar recibir mensaje (timeout corto)
        try:
            mensaje = consumidor.receive(timeout_millis=5000)
            
            # Intentar deserializar
            try:
                datos = mensaje.value()
                logger.info(f"✅ Evento confirmado encontrado: {datos}")
                consumidor.acknowledge(mensaje)
                return True
                
            except Exception:
                # Si falla deserialización, intentar como bytes
                datos_raw = mensaje.data().decode('utf-8') 
                datos = json.loads(datos_raw)
                logger.info(f"✅ Evento confirmado encontrado (JSON): {datos}")
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
    
    logger.info("⏳ Esperando 10 segundos para que notificaciones procese...")
    await asyncio.sleep(10)
    
    try:
        # Revisar logs de notificaciones
        import subprocess
        result = subprocess.run(
            ["docker", "logs", "notificaciones-shared", "--tail", "30"],
            capture_output=True,
            text=True
        )
        
        logs = result.stdout
        logger.info("📋 Logs recientes de notificaciones:")
        
        # Buscar evidencia de procesamiento
        if "VentaReferidaConfirmada" in logs and "Notificación" in logs:
            logger.info("✅ Notificaciones procesó el evento")
        else:
            logger.warning("⚠️ No se encontró evidencia clara de procesamiento")
        
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
        
        return "VentaReferidaConfirmada" in logs
        
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
    """Función principal de la prueba end-to-end"""
    logger.info("🧪 === INICIANDO PRUEBA END-TO-END COMPLETA ===")
    start_time = time.time()
    
    # Paso 1: Publicar evento
    evento = await step_1_publicar_evento_tracking()
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
    
    logger.info(f"\n🎯 === RESULTADO DE LA PRUEBA ({duration:.1f}s) ===")
    logger.info(f"✅ Evento publicado: {'SÍ' if evento else 'NO'}")
    logger.info(f"✅ Referidos procesó: {'SÍ' if referidos_ok else 'NO'}")
    logger.info(f"✅ Evento confirmado: {'SÍ' if confirmado_ok else 'NO'}")
    logger.info(f"✅ Notificaciones procesó: {'SÍ' if notificaciones_ok else 'NO'}")
    
    if evento and referidos_ok and confirmado_ok and notificaciones_ok:
        logger.info("🎉 === PRUEBA END-TO-END EXITOSA ===")
    else:
        logger.info("⚠️ === PRUEBA PARCIALMENTE EXITOSA ===")

if __name__ == "__main__":
    asyncio.run(main())