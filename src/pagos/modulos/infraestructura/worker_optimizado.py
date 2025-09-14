"""
Worker optimizado para el microservicio de Pagos.
Implementa consumo y publicación eficiente con Avro.
"""

import asyncio
import logging
import json
from datetime import datetime
from pulsar import Client
import pulsar
from pulsar.schema import AvroSchema, BytesSchema
from .repositorio_postgresql import RepositorioPagosPG, OutboxORM, PagoORM
from pagos.config.pulsar_config import settings
from pagos.schema.eventos_referidos import VentaReferidaConfirmada
from pagos.schema.eventos_pagos import PagoCompletado as PagoCompletadoAvro

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventProcessor:
    """Procesador de eventos que separa concerns de manera clara"""
    
    def __init__(self, repo: RepositorioPagosPG):
        self.repo = repo

    def procesar_venta_confirmada(self, venta: VentaReferidaConfirmada) -> PagoCompletadoAvro:
        """
        Procesa un evento de venta confirmada y retorna el evento de pago a publicar
        """
        with self.repo.SessionLocal() as session:
            # Buscar pago existente
            pago_orm = session.query(PagoORM).filter_by(
                idEvento=venta.idEvento, 
                estado="solicitado"
            ).first()
            
            if pago_orm:
                # Actualizar pago existente
                pago_orm.estado = "completado"
                if venta.fechaEvento:
                    pago_orm.fechaPago = datetime.fromisoformat(venta.fechaEvento.replace('Z', '+00:00'))
                else:
                    pago_orm.fechaPago = datetime.utcnow()
                session.commit()
                logger.info(f"Pago actualizado: {pago_orm.idPago}")
            else:
                # Crear nuevo pago
                from uuid import uuid4
                fecha_pago = datetime.utcnow()
                if venta.fechaEvento:
                    try:
                        fecha_pago = datetime.fromisoformat(venta.fechaEvento.replace('Z', '+00:00'))
                    except:
                        logger.warning(f"Error parseando fecha: {venta.fechaEvento}, usando fecha actual")
                        
                pago_orm = PagoORM(
                    idPago=str(uuid4()),
                    idEvento=venta.idEvento,
                    idSocio=venta.idSocio,
                    monto=venta.monto,
                    estado="completado",
                    fechaPago=fecha_pago
                )
                session.add(pago_orm)
                session.commit()
                logger.info(f"Nuevo pago creado: {pago_orm.idPago}")
            
            # Crear evento Avro de respuesta
            return PagoCompletadoAvro(
                idPago=pago_orm.idPago,
                idEvento=pago_orm.idEvento,
                idSocio=pago_orm.idSocio,
                monto=float(pago_orm.monto),
                estado="completado",
                fechaPago=pago_orm.fechaPago.isoformat()
            )

class AvroEventPublisher:
    """Publicador de eventos usando schemas Avro"""
    
    def __init__(self, pulsar_url: str):
        self.client = Client(pulsar_url)
        self.producers = {}
    
    def get_producer(self, topic: str, schema_class):
        """Obtiene o crea un productor para un tópico específico"""
        if topic not in self.producers:
            self.producers[topic] = self.client.create_producer(
                topic=topic,
                schema=AvroSchema(schema_class),
                batching_enabled=True,
                compression_type=pulsar.CompressionType.LZ4
            )
        return self.producers[topic]
    
    async def publish_pago_completado(self, evento: PagoCompletadoAvro):
        """Publica evento de pago completado con schema Avro"""
        producer = self.get_producer(settings.TOPIC_PAGOS, PagoCompletadoAvro)
        producer.send(evento, partition_key=evento.idPago)
        logger.info(f"Evento PagoCompletado publicado: {evento.idPago}")
    
    def close(self):
        """Cierra todas las conexiones"""
        for producer in self.producers.values():
            producer.close()
        self.client.close()

async def consumidor_optimizado(repo: RepositorioPagosPG):
    """
    Consumidor optimizado que usa Avro para input y output
    """
    logger.info("🚀 Iniciando consumidor optimizado...")
    
    # Inicializar componentes
    event_processor = EventProcessor(repo)
    publisher = AvroEventPublisher(settings.PULSAR_URL)
    
    try:
        # Cliente y consumidor con AvroSchema - igual que en referidos
        client = Client(settings.PULSAR_URL)
        consumer = client.subscribe(
            topic=settings.TOPIC_REFERIDO_CONFIRMADO,
            subscription_name="pagos-svc",
            consumer_type=pulsar.ConsumerType.Shared,
            schema=AvroSchema(VentaReferidaConfirmada),
            negative_ack_redelivery_delay_ms=5000  # Reintento en caso de error
        )
        
        logger.info("✅ Consumidor configurado con AvroSchema - patron referidos")
        
        while True:
            try:
                # Recibir mensaje con timeout
                msg = consumer.receive(timeout_millis=10000)
                
                if msg:
                    logger.info(f"📨 Mensaje recibido: {msg.message_id()}")
                    
                    # Obtener datos en crudo para debug
                    raw_data = msg.value()
                    properties = msg.properties()
                    
                    logger.info(f"� Datos en crudo: {raw_data}")
                    logger.info(f"🏷️ Propiedades: {properties}")
                    logger.info(f"📏 Tamaño: {len(raw_data) if raw_data else 0} bytes")
                    
                    # Intentar deserializar manualmente usando el schema
                    try:
                        avro_schema = AvroSchema(VentaReferidaConfirmada)
                        venta_confirmada = avro_schema._schema.from_json(raw_data.decode('utf-8') if isinstance(raw_data, bytes) else str(raw_data))
                        logger.info(f"✅ Deserialización manual exitosa: {venta_confirmada}")
                    except Exception as e:
                        logger.error(f"❌ Error en deserialización manual: {e}")
                        # Intentar como JSON directo
                        try:
                            json_data = json.loads(raw_data.decode('utf-8') if isinstance(raw_data, bytes) else raw_data)
                            logger.info(f"📋 Datos como JSON: {json_data}")
                        except Exception as e2:
                            logger.error(f"❌ Error al parsear como JSON: {e2}")
                    
                    # Confirmar mensaje para evitar redelivery
                    consumer.acknowledge(msg)
                    logger.info("✅ Mensaje confirmado")
                    
            except pulsar.Timeout:
                logger.debug("⏱️ Timeout esperando mensajes...")
                continue
            except Exception as e:
                logger.error(f"❌ Error procesando mensaje: {e}")
                # En caso de error, el mensaje será redelivered
                if 'msg' in locals():
                    consumer.negative_acknowledge(msg)
                continue
                
    except Exception as e:
        logger.error(f"❌ Error fatal en consumidor: {e}")
    finally:
        publisher.close()
        client.close()

async def despachador_outbox_optimizado(repo: RepositorioPagosPG):
    """
    Despachador outbox optimizado - maneja solo mensajes legacy JSON
    Los nuevos eventos van directo via Avro
    """
    client = Client(settings.PULSAR_URL)
    producer = client.create_producer(
        topic=settings.TOPIC_PAGOS,
        batching_enabled=True,
        compression_type=pulsar.CompressionType.LZ4
    )
    
    logger.info("📤 Despachador outbox iniciado (legacy JSON)")
    
    while True:
        try:
            with repo.SessionLocal() as session:
                # Procesar mensajes pendientes (principalmente legacy)
                items = session.query(OutboxORM).filter_by(
                    status="PENDING"
                ).limit(settings.OUTBOX_BATCH_SIZE).all()
                
                for item in items:
                    try:
                        producer.send(
                            item.payload.encode("utf-8"),
                            partition_key=item.key
                        )
                        item.status = "SENT"
                        session.commit()
                        logger.info(f"📤 Outbox item enviado: {item.id}")
                    except Exception as e:
                        logger.error(f"❌ Error enviando outbox {item.id}: {e}")
                        
        except Exception as e:
            logger.error(f"❌ Error en despachador outbox: {e}")
            
        await asyncio.sleep(5)  # Menos frecuente ya que Avro es directo
    
    client.close()

async def main_worker():
    """
    Worker principal optimizado
    """
    logger.info("🚀 Iniciando worker de pagos optimizado...")
    
    repo = RepositorioPagosPG(settings.DB_URL)
    
    # Ejecutar ambos workers en paralelo
    await asyncio.gather(
        consumidor_optimizado(repo),
        despachador_outbox_optimizado(repo)
    )

if __name__ == "__main__":
    asyncio.run(main_worker())