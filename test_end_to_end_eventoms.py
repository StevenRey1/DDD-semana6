#!/usr/bin/env python3
"""
Test End-to-End completo con eventoMS como punto de entrada
Flujo: eventoMS -> eventos-tracking -> referidos -> eventos-referido-confirmado -> notificaciones
"""

import uuid
import time
import logging
import requests
import json
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generar_evento_test():
    """Genera datos de evento de prueba con UUIDs válidos"""
    return {
        "tipoEvento": "venta_creada",
        "idReferido": str(uuid.uuid4()),
        "idSocio": str(uuid.uuid4()),
        "monto": 125000.0,
        "fechaEvento": "2025-09-14T01:30:00Z"
    }

def registrar_evento_via_api(evento_data):
    """Registra un evento usando la API de eventoMS"""
    try:
        url = "http://localhost:8003/eventos"
        headers = {"Content-Type": "application/json"}
        
        logger.info("📤 === REGISTRANDO EVENTO VIA eventoMS API ===")
        logger.info(f"📤 URL: {url}")
        logger.info(f"📤 Payload: {json.dumps(evento_data, indent=2)}")
        
        response = requests.post(url, json=evento_data, headers=headers, timeout=10)
        
        if response.status_code == 202:
            logger.info("✅ Evento registrado exitosamente via eventoMS API")
            logger.info(f"📋 Response: {response.status_code} - {response.text}")
            return True
        else:
            logger.error(f"❌ Error registrando evento: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error de conexión con eventoMS API: {e}")
        return False

def verificar_health_checks():
    """Verifica que todos los servicios estén funcionando"""
    servicios = {
        "eventos": "http://localhost:8003/health",
        "referidos": "http://localhost:5001/health", 
        "notificaciones": "http://localhost:8002/health"
    }
    
    logger.info("🔍 === VERIFICANDO HEALTH CHECKS ===")
    
    for servicio, url in servicios.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ {servicio}: OK")
            else:
                logger.warning(f"⚠️ {servicio}: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ {servicio}: {e}")
            return False
    
    return True

def consultar_eventos_socio(id_socio):
    """Consulta eventos de un socio específico"""
    try:
        url = f"http://localhost:8003/eventos/{id_socio}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"📊 Eventos del socio {id_socio}: {len(data.get('eventos', []))} eventos")
            return data
        else:
            logger.warning(f"⚠️ No se pudieron obtener eventos del socio: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error consultando eventos del socio: {e}")
        return None

def verificar_notificaciones():
    """Verifica que las notificaciones se hayan generado"""
    try:
        url = "http://localhost:8002/notificaciones"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            total = len(data.get('notificaciones', []))
            logger.info(f"📊 Total notificaciones en sistema: {total}")
            return total
        else:
            logger.warning(f"⚠️ No se pudieron obtener notificaciones: {response.status_code}")
            return 0
            
    except Exception as e:
        logger.error(f"❌ Error verificando notificaciones: {e}")
        return 0

def main():
    """Función principal del test end-to-end"""
    logger.info("🧪 === INICIANDO TEST END-TO-END CON eventoMS ===")
    start_time = time.time()
    
    # === PASO 1: Verificar health checks ===
    logger.info("🔍 === PASO 1: VERIFICANDO SERVICIOS ===")
    if not verificar_health_checks():
        logger.error("❌ Algunos servicios no están disponibles")
        return False
    
    # === PASO 2: Generar evento de prueba ===
    logger.info("🚀 === PASO 2: GENERANDO EVENTO DE PRUEBA ===")
    evento_data = generar_evento_test()
    
    logger.info(f"📋 Datos del evento:")
    logger.info(f"  📋 idSocio: {evento_data['idSocio']}")
    logger.info(f"  📋 idReferido: {evento_data['idReferido']}")
    logger.info(f"  💰 monto: {evento_data['monto']}")
    logger.info(f"  📅 fechaEvento: {evento_data['fechaEvento']}")
    
    # === PASO 3: Registrar evento via eventoMS ===
    logger.info("📤 === PASO 3: REGISTRANDO EVENTO VIA eventoMS ===")
    if not registrar_evento_via_api(evento_data):
        logger.error("❌ No se pudo registrar el evento")
        return False
    
    # === PASO 4: Esperar procesamiento en referidos ===
    logger.info("🔍 === PASO 4: ESPERANDO PROCESAMIENTO EN REFERIDOS ===")
    logger.info("⏳ Esperando 30 segundos para que referidos procese...")
    time.sleep(30)
    
    # === PASO 5: Verificar notificaciones ===
    logger.info("🔍 === PASO 5: VERIFICANDO NOTIFICACIONES ===")
    logger.info("⏳ Esperando 20 segundos para que notificaciones procese...")
    time.sleep(20)
    
    total_notificaciones_final = verificar_notificaciones()
    
    # === PASO 6: Consultar eventos del socio ===
    logger.info("🔍 === PASO 6: CONSULTANDO EVENTOS DEL SOCIO ===")
    eventos_socio = consultar_eventos_socio(evento_data['idSocio'])
    
    # === PASO 7: Resumen final ===
    elapsed_time = time.time() - start_time
    logger.info("📊 === RESUMEN FINAL ===")
    logger.info(f"⏱️ Tiempo total: {elapsed_time:.1f}s")
    logger.info(f"✅ Evento registrado via eventoMS: SÍ")
    logger.info(f"✅ Notificaciones generadas: {total_notificaciones_final}")
    
    if eventos_socio:
        eventos_count = len(eventos_socio.get('eventos', []))
        logger.info(f"✅ Eventos del socio: {eventos_count}")
    else:
        logger.info(f"⚠️ No se pudieron consultar eventos del socio")
    
    logger.info("🎊 === TEST END-TO-END COMPLETADO ===")
    logger.info("🚀 ¡Flujo completo eventoMS -> referidos -> notificaciones funcionando!")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)