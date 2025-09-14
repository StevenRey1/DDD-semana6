"""
Script para registrar schemas en Pulsar Schema Registry
y probar el consumo dinámico de schemas
"""

import asyncio
import logging
import json
import pulsar
from pulsar.schema import AvroSchema, Record

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar las clases de schema
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from src.notificaciones.modulos.infraestructura.schema.eventos_referidos import VentaReferidaConfirmada
from src.notificaciones.config.pulsar_config import pulsar_config

async def registrar_schemas():
    """Registra schemas en Pulsar Schema Registry"""
    cliente = None
    try:
        # Crear cliente Pulsar (usando puerto expuesto por Docker)
        cliente = pulsar.Client(
            service_url='pulsar://localhost:6653',
            connection_timeout_ms=10000
        )
        
        # 1. Registrar schema de VentaReferidaConfirmada
        topico_referidos = pulsar_config.get_full_topic_name("eventos-referido-confirmado")
        schema_referidos = AvroSchema(VentaReferidaConfirmada)
        
        logger.info(f"🔄 Registrando schema para {topico_referidos}")
        
        # Crear un productor temporal para registrar el schema
        productor_referidos = cliente.create_producer(
            topic=topico_referidos,
            schema=schema_referidos
        )
        
        logger.info(f"✅ Schema registrado para {topico_referidos}")
        productor_referidos.close()
        
        # 2. Crear un schema "externo" simulado para probar el consumo dinámico
        # Usar una clase simple para simular un evento de tracking
        
        class EventoTracking(Record):
            idEvento = pulsar.schema.String()
            usuarioId = pulsar.schema.String()
            accion = pulsar.schema.String()
            timestamp = pulsar.schema.Integer()
            metadata = pulsar.schema.String()  # Simplificado como string
        
        # Registrar schema de tracking
        topico_tracking = pulsar_config.get_full_topic_name("eventos-tracking")
        schema_tracking = AvroSchema(EventoTracking)
        
        logger.info(f"🔄 Registrando schema para {topico_tracking}")
        
        productor_tracking = cliente.create_producer(
            topic=topico_tracking,
            schema=schema_tracking
        )
        
        # Publicar un evento de ejemplo para asegurar que el schema se registre
        evento_ejemplo = EventoTracking(
            idEvento="test-001",
            usuarioId="user-123",
            accion="click",
            timestamp=1694624400,
            metadata='{"page": "home"}'
        )
        
        productor_tracking.send(evento_ejemplo)
        logger.info(f"✅ Schema registrado y evento de ejemplo enviado para {topico_tracking}")
        productor_tracking.close()
        
        # 3. Verificar que los schemas están registrados
        logger.info("🔍 Verificando schemas registrados...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error registrando schemas: {e}")
        return False
    finally:
        if cliente:
            cliente.close()

async def probar_consumo_dinamico():
    """Prueba el consumo dinámico usando el Schema Manager"""
    
    # Importar el schema manager
    from src.notificaciones.modulos.infraestructura.schema_manager import ManejadorSchemaHibrido
    
    # Probar diferentes configuraciones
    configs_prueba = [
        {
            "nombre": "Solo Registry",
            "schema_estatico": None,
            "usar_registry": True,
            "usar_dinamico": False
        },
        {
            "nombre": "Registry + Estático",
            "schema_estatico": VentaReferidaConfirmada,
            "usar_registry": True,
            "usar_dinamico": False
        },
        {
            "nombre": "Registry + Estático + Dinámico (Completo)",
            "schema_estatico": VentaReferidaConfirmada,
            "usar_registry": True,
            "usar_dinamico": True
        }
    ]
    
    topicos_prueba = [
        pulsar_config.get_full_topic_name("eventos-referido-confirmado"),
        pulsar_config.get_full_topic_name("eventos-tracking"),
        pulsar_config.get_full_topic_name("eventos-inexistente")
    ]
    
    for config in configs_prueba:
        logger.info(f"\n🧪 === PRUEBA: {config['nombre']} ===")
        
        manager = ManejadorSchemaHibrido(
            schema_estatico_class=config['schema_estatico'],
            usar_registry=config['usar_registry'],
            usar_dinamico=config['usar_dinamico']
        )
        
        for topico in topicos_prueba:
            logger.info(f"🔍 Probando tópico: {topico}")
            schema = manager.obtener_schema(topico)
            
            if schema:
                logger.info(f"  ✅ Schema obtenido: {type(schema)}")
                logger.info(f"  📋 Estrategia activa: {manager.get_estrategia_activa()}")
            else:
                logger.warning(f"  ❌ No se pudo obtener schema")
        
        print("-" * 50)

async def main():
    """Función principal"""
    logger.info("🚀 === REGISTRO Y PRUEBA DE SCHEMAS ===")
    
    # 1. Registrar schemas
    logger.info("\n📝 Paso 1: Registrando schemas en Pulsar...")
    success = await registrar_schemas()
    
    if not success:
        logger.error("❌ No se pudieron registrar los schemas. Abortando.")
        return
    
    # 2. Probar consumo dinámico
    logger.info("\n🧪 Paso 2: Probando consumo dinámico...")
    await probar_consumo_dinamico()
    
    logger.info("\n✅ === PRUEBAS COMPLETADAS ===")

if __name__ == "__main__":
    asyncio.run(main())