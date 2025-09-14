"""
Script para simular eventos de referidos y probar el Schema Manager de notificaciones
"""

import asyncio
import logging
import json
import pulsar
from pulsar.schema import AvroSchema

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def simular_eventos_referidos():
    """Simula eventos de referidos para probar notificaciones"""
    
    try:
        # Conectar a Pulsar
        cliente = pulsar.Client('pulsar://localhost:6653')
        
        logger.info("🚀 Conectado a Pulsar, simulando eventos...")
        
        # 1. Evento de referido creado (sin schema - para probar fallback dinámico)
        topico_eventos = "persistent://public/default/eventos-tracking"
        
        productor_eventos = cliente.create_producer(
            topic=topico_eventos
        )
        
        evento_tracking = {
            "id_evento": "evt-001",
            "tipo_evento": "ReferidoCreado", 
            "id_socio": "e220f6d1-2d6b-43ba-b6fc-49790e85d0c2",
            "id_referido": "ref-001",
            "nombre_referido": "Juan Pérez",
            "email_referido": "juan.perez@test.com",
            "estado": "pendiente",
            "fecha_evento": "2025-09-14T01:20:00Z",
            "datos_adicionales": {
                "canal": "web",
                "campana": "referidos-2025"
            }
        }
        
        logger.info(f"📤 Enviando evento de tracking: {evento_tracking['tipo_evento']}")
        
        # Enviar como JSON sin schema (probar deserialización dinámica)
        productor_eventos.send(json.dumps(evento_tracking).encode('utf-8'))
        
        logger.info("✅ Evento de tracking enviado")
        
        # 2. Simular evento de VentaReferidaConfirmada (con schema estático)
        from src.notificaciones.modulos.infraestructura.schema.eventos_referidos import VentaReferidaConfirmada
        
        topico_confirmados = "persistent://public/default/eventos-referido-confirmado"
        schema_confirmado = AvroSchema(VentaReferidaConfirmada)
        
        productor_confirmados = cliente.create_producer(
            topic=topico_confirmados,
            schema=schema_confirmado
        )
        
        evento_confirmado = VentaReferidaConfirmada(
            idEvento="conf-001",
            idSocio="e220f6d1-2d6b-43ba-b6fc-49790e85d0c2",
            monto=50000.0,
            fechaEvento="2025-09-14T01:21:00Z"
        )
        
        logger.info(f"📤 Enviando evento confirmado con schema: VentaReferidaConfirmada")
        
        productor_confirmados.send(evento_confirmado)
        
        logger.info("✅ Evento confirmado enviado")
        
        # 3. Evento de pago (para probar el consumidor de pagos)
        topico_pagos = "persistent://public/default/eventos-pagos"
        
        productor_pagos = cliente.create_producer(
            topic=topico_pagos
        )
        
        evento_pago = {
            "id_pago": "pago-001",
            "id_socio": "e220f6d1-2d6b-43ba-b6fc-49790e85d0c2",
            "monto": 25000.0,
            "estado": "completado",
            "metodo_pago": "tarjeta_credito",
            "fecha_pago": "2025-09-14T01:22:00Z"
        }
        
        logger.info(f"📤 Enviando evento de pago: {evento_pago['estado']}")
        
        productor_pagos.send(json.dumps(evento_pago).encode('utf-8'))
        
        logger.info("✅ Evento de pago enviado")
        
        # Cerrar conexiones
        productor_eventos.close()
        productor_confirmados.close()
        productor_pagos.close()
        cliente.close()
        
        logger.info("🎉 Todos los eventos enviados exitosamente")
        
        # Esperar unos segundos para que los consumidores procesen
        logger.info("⏳ Esperando 10 segundos para que se procesen los eventos...")
        await asyncio.sleep(10)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error simulando eventos: {e}")
        return False

async def verificar_notificaciones():
    """Verifica que las notificaciones se hayan creado"""
    
    import requests
    
    try:
        logger.info("🔍 Verificando notificaciones creadas...")
        
        response = requests.get("http://localhost:8002/notificaciones")
        
        if response.status_code == 200:
            notificaciones = response.json()
            logger.info(f"📊 Total notificaciones: {len(notificaciones.get('datos', []))}")
            
            for notif in notificaciones.get('datos', [])[:3]:  # Mostrar las primeras 3
                logger.info(f"  📧 {notif.get('titulo', 'Sin título')}: {notif.get('mensaje', 'Sin mensaje')[:50]}...")
        else:
            logger.warning(f"⚠️ No se pudieron obtener notificaciones: {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Error verificando notificaciones: {e}")

async def main():
    """Función principal"""
    logger.info("🧪 === SIMULACIÓN DE EVENTOS PARA SCHEMA MANAGER ===")
    
    # 1. Simular eventos
    success = await simular_eventos_referidos()
    
    if success:
        # 2. Verificar notificaciones
        await verificar_notificaciones()
        
        logger.info("✅ === SIMULACIÓN COMPLETADA ===")
    else:
        logger.error("❌ === SIMULACIÓN FALLÓ ===")

if __name__ == "__main__":
    asyncio.run(main())