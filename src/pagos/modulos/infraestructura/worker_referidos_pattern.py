"""
Worker optimizado siguiendo el patrón exacto de referidos para consumir eventos Avro
"""

import asyncio
import json
import logging
import traceback
from datetime import datetime
from uuid import uuid4

import pulsar
from pulsar import Client, ConsumerType
from pulsar.schema import AvroSchema
from sqlalchemy.orm import sessionmaker

from pagos.config.pulsar_config import Settings
from pagos.modulos.infraestructura.repositorio_postgresql import RepositorioPagosPG, PagoORM
from pagos.schema.eventos_referidos import VentaReferidaConfirmada
from pagos.schema.eventos_pagos import PagoCompletado as PagoCompletadoAvro

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instanciar settings
settings = Settings()

async def consumidor_patron_referidos(repo: RepositorioPagosPG):
    """
    Consumidor que sigue exactamente el patrón de referidos para eventos Avro
    """
    logger.info("🚀 Iniciando consumidor con patrón referidos...")
    
    cliente = None
    try:
        # Configurar cliente igual que referidos
        cliente = pulsar.Client(settings.PULSAR_URL)
        
        # Configurar consumidor con AvroSchema igual que referidos
        consumidor = cliente.subscribe(
            settings.TOPIC_REFERIDO_CONFIRMADO,
            consumer_type=pulsar.ConsumerType.Shared,
            subscription_name='pagos-svc',
            schema=AvroSchema(VentaReferidaConfirmada),
            receiver_queue_size=1000,
            max_total_receiver_queue_size_across_partitions=50000,
            consumer_name='pagos-consumer'
        )

        logger.info("✅ Consumidor de eventos-referido-confirmado iniciado para pagos")
        
        while True:
            try:
                mensaje = consumidor.receive()
                evento_data = mensaje.value()
                logger.info(f"📨 VentaReferidaConfirmada recibido: {evento_data}")
                
                # Acceder directamente a los campos - automático con Avro
                logger.info(f"📝 Procesando pago:")
                logger.info(f"   - idEvento: {evento_data.idEvento}")
                logger.info(f"   - idSocio: {evento_data.idSocio}")
                logger.info(f"   - monto: {evento_data.monto}")
                logger.info(f"   - fechaEvento: {evento_data.fechaEvento}")
                
                # Procesar pago en base de datos
                with repo.SessionLocal() as session:
                    # Verificar si ya existe el pago
                    pago_existente = session.query(PagoORM).filter_by(idEvento=evento_data.idEvento).first()
                    
                    if not pago_existente:
                        # Crear nuevo pago
                        fecha_pago = datetime.now()
                        
                        pago_orm = PagoORM(
                            idPago=str(uuid4()),
                            idEvento=evento_data.idEvento,
                            idSocio=evento_data.idSocio,
                            monto=evento_data.monto,
                            estado="completado",
                            fechaPago=fecha_pago
                        )
                        session.add(pago_orm)
                        session.commit()
                        logger.info(f"💰 Nuevo pago creado: {pago_orm.idPago}")
                        
                        # Publicar evento de pago completado
                        pago_completado = PagoCompletadoAvro(
                            idPago=pago_orm.idPago,
                            idEvento=pago_orm.idEvento,
                            idSocio=pago_orm.idSocio,
                            monto=float(pago_orm.monto),
                            estado="completado",
                            fechaPago=pago_orm.fechaPago.isoformat()
                        )
                        
                        # Publicar usando Avro
                        producer = cliente.create_producer(
                            topic='eventos-pagos',
                            schema=AvroSchema(PagoCompletadoAvro)
                        )
                        producer.send(pago_completado)
                        producer.close()
                        
                        logger.info(f"📤 Evento PagoCompletado publicado: {pago_completado.idPago}")
                    else:
                        logger.info(f"⚠️ Pago ya existe para evento: {evento_data.idEvento}")
                
                # Confirmar mensaje
                consumidor.acknowledge(mensaje)
                logger.info("✅ Mensaje procesado y confirmado")
                
            except Exception as e:
                # En caso de error, negar el mensaje para redelivery
                if 'mensaje' in locals():
                    consumidor.negative_acknowledge(mensaje)
                continue
                
    except Exception as e:
        logger.error(f"❌ Error fatal en consumidor: {e}")
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
    finally:
        if cliente:
            cliente.close()

if __name__ == "__main__":
    repo = RepositorioPagosPG(settings.DB_URL)
    asyncio.run(consumidor_patron_referidos(repo))