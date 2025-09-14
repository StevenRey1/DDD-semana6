#!/usr/bin/env python3
"""
Script para probar el Schema Manager híbrido
"""

import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_schema_manager():
    """Prueba básica del Schema Manager"""
    try:
        from modulos.infraestructura.schema_manager import ManejadorSchemaHibrido
        from modulos.infraestructura.schema.v1.eventos_referidos import VentaReferidaConfirmada
        
        logger.info("🚀 Iniciando prueba del Schema Manager...")
        
        # Test 1: Schema Manager sin schema estático
        logger.info("📋 Test 1: Schema Manager básico")
        manager1 = ManejadorSchemaHibrido()
        logger.info(f"✅ Schema Manager creado con {len(manager1.proveedores)} proveedores")
        
        # Test 2: Schema Manager con schema estático
        logger.info("📋 Test 2: Schema Manager con schema estático")
        manager2 = ManejadorSchemaHibrido(
            schema_estatico_class=VentaReferidaConfirmada,
            usar_registry=True,
            usar_dinamico=True
        )
        logger.info(f"✅ Schema Manager con estático creado con {len(manager2.proveedores)} proveedores")
        
        # Test 3: Intentar obtener schema para un tópico
        logger.info("📋 Test 3: Obtener schema para tópico")
        topico_test = "eventos-referido-confirmado"
        schema = manager2.obtener_schema(topico_test)
        
        if schema:
            logger.info(f"✅ Schema obtenido para {topico_test}: {type(schema)}")
            logger.info(f"🔍 Estrategia activa: {manager2.get_estrategia_activa()}")
        else:
            logger.info(f"⚠️ No se pudo obtener schema para {topico_test}")
        
        logger.info("🎉 Todas las pruebas completadas")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_schema_manager()
    sys.exit(0 if success else 1)