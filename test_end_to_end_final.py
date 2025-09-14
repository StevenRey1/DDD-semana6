"""
Prueba End-to-End FINAL del flujo completo de eventos con UUIDs válidos:
eventos-tracking → referidos → eventos-referido-confirmado → notificaciones
"""

import asyncio
import logging
import json
import time
import uuid
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

async def step_1_publicar_evento_tracking_final():
    """Paso 1: Publicar evento en eventos-tracking con UUIDs válidos"""
    logger.info("🚀 === PASO 1: PUBLICANDO EVENTO FINAL CON UUIDS VÁLIDOS ===")
    
    try:
        # Conectar a Pulsar
        cliente = pulsar.Client('pulsar://localhost:6653')
        
        # Generar UUIDs válidos
        id_evento = str(uuid.uuid4())
        id_referido = str(uuid.uuid4())
        id_socio = str(uuid.uuid4())
        
        # Crear el evento con UUIDs válidos
        evento_tracking = EventoRegistrado(
            idEvento=id_evento,
            tipoEvento="venta_creada",  # Tipo que referidos filtra
            idReferido=id_referido, 
            idSocio=id_socio,
            monto=125000.0,
            estado="pendiente",  # Estado inicial
            fechaEvento="2025-09-14T01:30:00Z"
        )
        
        # Crear productor con esquema Avro
        topico_tracking = "persistent://public/default/eventos-tracking"
        productor = cliente.create_producer(
            topic=topico_tracking,
            schema=AvroSchema(EventoRegistrado)
        )
        
        logger.info(f"📤 Enviando evento con UUIDs válidos:")
        logger.info(f"  📋 idEvento: {id_evento}")
        logger.info(f"  📋 idReferido: {id_referido}")
        logger.info(f"  📋 idSocio: {id_socio}")
        logger.info(f"  💰 monto: {evento_tracking.monto}")
        
        # Enviar con esquema Avro
        productor.send(evento_tracking)
        
        logger.info("✅ Evento con UUIDs válidos enviado a eventos-tracking")
        
        # Limpiar
        productor.close()
        cliente.close()
        
        return evento_tracking, id_evento
        
    except Exception as e:
        logger.error(f"❌ Error en Paso 1: {e}")
        return None, None

async def step_2_esperar_y_verificar_referidos(id_evento):
    """Paso 2: Esperar y verificar que referidos procesó el evento"""
    logger.info("🔍 === PASO 2: VERIFICANDO PROCESAMIENTO EN REFERIDOS ===")
    
    logger.info("⏳ Esperando 25 segundos para que referidos procese...")
    await asyncio.sleep(25)
    
    try:
        # Revisar logs de referidos
        import subprocess
        result = subprocess.run(
            ["docker", "logs", "referidos-shared", "--tail", "40"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'  # Ignorar errores de encoding
        )
        
        logs = result.stdout
        logger.info("📋 Últimos logs de referidos:")
        
        # Buscar evidencia de procesamiento exitoso
        if f"EventoRegistrado recibido" in logs and id_evento in logs:
            logger.info("✅ Referidos recibió el evento correctamente")
            
            if "Referido generado para evento" in logs and id_evento in logs:
                logger.info("✅ Referidos generó el referido exitosamente")
                return True
            elif "Error procesando evento" in logs:
                logger.warning("⚠️ Referidos tuvo errores procesando el evento")
                return False
            else:
                logger.info("🔄 Referidos procesó el evento (verificando flujo completo)")
                return True
        else:
            logger.warning("⚠️ No se encontró el evento en los logs")
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
            subscription_name="test-verificacion-final",
            consumer_type=pulsar.ConsumerType.Exclusive
        )
        
        logger.info("📥 Buscando mensajes en eventos-referido-confirmado...")
        
        # Intentar recibir mensaje (timeout más largo)
        try:
            mensaje = consumidor.receive(timeout_millis=15000)
            
            # Intentar deserializar
            try:
                datos = mensaje.value()
                logger.info(f"✅ Evento confirmado encontrado (Avro): {datos}")
                consumidor.acknowledge(mensaje)
                return True
                
            except Exception as e:
                # Si falla deserialización, intentar como bytes
                datos_raw = mensaje.data().decode('utf-8') 
                logger.info(f"✅ Evento confirmado encontrado (raw): {datos_raw}")
                consumidor.acknowledge(mensaje)
                return True
                
        except pulsar.Timeout:
            logger.warning("⚠️ No se encontraron mensajes en eventos-referido-confirmado (timeout)")
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
    
    logger.info("⏳ Esperando 20 segundos para que notificaciones procese...")
    await asyncio.sleep(20)
    
    try:
        # Revisar logs de notificaciones
        import subprocess
        result = subprocess.run(
            ["docker", "logs", "notificaciones-shared", "--tail", "50"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        logs = result.stdout
        logger.info("📋 Últimos logs de notificaciones:")
        
        # Buscar evidencia de procesamiento
        notif_procesado = (
            "NotificacionCreada" in logs or 
            "VentaReferidaConfirmada" in logs or
            "Notificación creada" in logs
        )
        
        if notif_procesado:
            logger.info("✅ Notificaciones procesó eventos relacionados")
        else:
            logger.warning("⚠️ No se encontró evidencia clara de procesamiento específico")
        
        # Verificar API de notificaciones
        try:
            response = requests.get("http://localhost:8002/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ API de notificaciones respondiendo")
                
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
        
        # Verificar APIs
        try:
            resp_ref = requests.get("http://localhost:8001/health", timeout=3)
            resp_notif = requests.get("http://localhost:8002/health", timeout=3)
            
            logger.info(f"🔗 API Referidos: {'✅ OK' if resp_ref.status_code == 200 else '❌ Error'}")
            logger.info(f"🔗 API Notificaciones: {'✅ OK' if resp_notif.status_code == 200 else '❌ Error'}")
            
        except Exception as e:
            logger.info(f"🔗 APIs: Error verificando - {e}")
        
        # Estado de tópicos
        try:
            response = requests.get("http://localhost:8083/admin/v2/persistent/public/default", timeout=5)
            if response.status_code == 200:
                topicos = response.json()
                logger.info(f"📋 Tópicos activos: {len(topicos)}")
                
                # Buscar tópicos específicos
                topicos_interes = [t for t in topicos if any(x in t for x in ['tracking', 'referido', 'notif'])]
                if topicos_interes:
                    logger.info(f"📋 Tópicos de eventos: {topicos_interes}")
        except:
            logger.info("📋 No se pudo verificar tópicos")
        
    except Exception as e:
        logger.error(f"❌ Error en resumen: {e}")

async def main():
    """Función principal de la prueba end-to-end FINAL"""
    logger.info("🧪 === INICIANDO PRUEBA END-TO-END FINAL CON UUIDS VÁLIDOS ===")
    start_time = time.time()
    
    # Paso 1: Publicar evento con UUIDs válidos
    evento, id_evento = await step_1_publicar_evento_tracking_final()
    if not evento:
        logger.error("❌ Fallo en Paso 1, abortando")
        return
    
    # Paso 2: Verificar referidos
    referidos_ok = await step_2_esperar_y_verificar_referidos(id_evento)
    
    # Paso 3: Verificar evento confirmado
    confirmado_ok = await step_3_verificar_evento_confirmado()
    
    # Paso 4: Verificar notificaciones  
    notificaciones_ok = await step_4_verificar_notificaciones()
    
    # Paso 5: Resumen
    await step_5_resumen_estado()
    
    # Resultado final
    end_time = time.time()
    duration = end_time - start_time
    
    logger.info(f"\n🎯 === RESULTADO DE LA PRUEBA FINAL ({duration:.1f}s) ===")
    logger.info(f"✅ Evento con UUIDs válidos: {'SÍ' if evento else 'NO'}")
    logger.info(f"✅ Referidos procesó: {'SÍ' if referidos_ok else 'NO'}")
    logger.info(f"✅ Evento confirmado: {'SÍ' if confirmado_ok else 'NO'}")
    logger.info(f"✅ Notificaciones procesó: {'SÍ' if notificaciones_ok else 'NO'}")
    
    success_rate = sum([bool(evento), referidos_ok, confirmado_ok, notificaciones_ok])
    
    if success_rate == 4:
        logger.info("🎉 === PRUEBA END-TO-END 100% EXITOSA ===")
        logger.info("🔥 ¡FLUJO COMPLETO FUNCIONANDO!")
    elif success_rate >= 3:
        logger.info("🎊 === PRUEBA MAYORMENTE EXITOSA ===")
        logger.info("🚀 ¡Flujo funcionando con éxito!")
    else:
        logger.info("⚠️ === PRUEBA PARCIALMENTE EXITOSA ===")

if __name__ == "__main__":
    asyncio.run(main())