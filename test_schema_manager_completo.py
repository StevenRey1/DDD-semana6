"""
Script para probar el Schema Manager híbrido con schemas reales en Pulsar
"""

import asyncio
import logging
import sys
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agregar el directorio del proyecto al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'notificaciones'))

async def probar_schema_manager():
    """Prueba el Schema Manager híbrido con diferentes configuraciones"""
    
    # Importar las clases necesarias
    from modulos.infraestructura.schema_manager import ManejadorSchemaHibrido
    from modulos.infraestructura.schema.eventos_referidos import VentaReferidaConfirmada
    from seedworks.infraestructura.utils import validar_conexion_schema_registry
    
    logger.info("🧪 === PRUEBA DEL SCHEMA MANAGER HÍBRIDO ===")
    
    # Verificar conectividad con Schema Registry
    registry_disponible = validar_conexion_schema_registry()
    logger.info(f"📡 Schema Registry disponible: {registry_disponible}")
    
    # Definir tópicos de prueba
    topicos_prueba = [
        "persistent://public/default/eventos-referido-confirmado",  # Debe encontrar en Registry
        "persistent://public/default/eventos-tracking",             # Debe encontrar en Registry (EventoRegistrado)
        "persistent://public/default/eventos-inexistente",          # No existe, debe usar fallback
    ]
    
    # Configuraciones de prueba
    configs_prueba = [
        {
            "nombre": "Solo Registry",
            "schema_estatico": None,
            "usar_registry": True,
            "usar_dinamico": False
        },
        {
            "nombre": "Registry + Estático (VentaReferidaConfirmada)",
            "schema_estatico": VentaReferidaConfirmada,
            "usar_registry": True,
            "usar_dinamico": False
        },
        {
            "nombre": "Fallback Completo (Registry + Estático + Dinámico)",
            "schema_estatico": VentaReferidaConfirmada,
            "usar_registry": True,
            "usar_dinamico": True
        }
    ]
    
    for config in configs_prueba:
        logger.info(f"\n🔬 === CONFIGURACIÓN: {config['nombre']} ===")
        
        try:
            manager = ManejadorSchemaHibrido(
                schema_estatico_class=config['schema_estatico'],
                usar_registry=config['usar_registry'],
                usar_dinamico=config['usar_dinamico']
            )
            
            logger.info(f"✅ Schema Manager creado con {len(manager.proveedores)} proveedores")
            
            for topico in topicos_prueba:
                logger.info(f"🔍 Probando tópico: {topico}")
                
                try:
                    schema = manager.obtener_schema(topico)
                    
                    if schema:
                        logger.info(f"  ✅ Schema obtenido: {type(schema)}")
                        estrategia = manager.get_estrategia_activa()
                        logger.info(f"  📋 Estrategia activa: {estrategia}")
                        
                        # Mostrar información adicional del schema
                        if hasattr(schema, '_schema_class'):
                            logger.info(f"  📄 Clase del schema: {schema._schema_class.__name__}")
                        
                    else:
                        logger.warning(f"  ❌ No se pudo obtener schema")
                        
                except Exception as e:
                    logger.error(f"  ❌ Error obteniendo schema: {e}")
            
            print("-" * 70)
            
        except Exception as e:
            logger.error(f"❌ Error creando Schema Manager: {e}")
    
    logger.info("\n✅ === PRUEBAS DEL SCHEMA MANAGER COMPLETADAS ===")

async def probar_consulta_directa_registry():
    """Prueba consulta directa al Schema Registry"""
    
    logger.info("\n🔎 === CONSULTA DIRECTA AL SCHEMA REGISTRY ===")
    
    from seedworks.infraestructura.utils import obtener_schema_desde_registry, consultar_schema_registry
    
    # Consultar schemas disponibles
    try:
        # Intentar consultar algunos tópicos conocidos
        logger.info("📚 Consultando schemas conocidos en Registry:")
        topicos_conocidos = [
            "persistent://public/default/eventos-referido-confirmado",
            "persistent://public/default/eventos-tracking",
        ]
        
        schemas_encontrados = 0
        for topico in topicos_conocidos:
            schema_info = consultar_schema_registry(topico)
            if schema_info:
                schemas_encontrados += 1
                logger.info(f"  ✅ {topico}: schema disponible")
            else:
                logger.info(f"  ❌ {topico}: schema no encontrado")
        
        logger.info(f"📊 Total schemas encontrados: {schemas_encontrados}/{len(topicos_conocidos)}")
        
    except Exception as e:
        logger.error(f"❌ Error consultando schemas: {e}")
    
    # Probar obtener schemas específicos
    topicos_test = [
        "persistent://public/default/eventos-referido-confirmado",
        "persistent://public/default/eventos-tracking"
    ]
    
    for topico in topicos_test:
        try:
            logger.info(f"\n🔍 Consultando schema para {topico}")
            schema = obtener_schema_desde_registry(topico)
            
            if schema:
                logger.info(f"  ✅ Schema obtenido: {type(schema)}")
            else:
                logger.warning(f"  ❌ No se encontró schema")
                
        except Exception as e:
            logger.error(f"  ❌ Error: {e}")

async def main():
    """Función principal"""
    logger.info("🚀 === PRUEBAS COMPLETAS DEL SISTEMA DE SCHEMAS ===")
    
    # 1. Probar consulta directa al registry
    await probar_consulta_directa_registry()
    
    # 2. Probar Schema Manager híbrido
    await probar_schema_manager()
    
    logger.info("\n🎉 === TODAS LAS PRUEBAS COMPLETADAS ===")

if __name__ == "__main__":
    asyncio.run(main())