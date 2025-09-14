"""
Worker de Mensajería para el microservicio de Pagos.
Implementa el patrón Outbox y maneja la comunicación asíncrona mediante Apache Pulsar.
"""

import asyncio
import json
from datetime import datetime
from pulsar import Client
from .repositorio_postgresql import RepositorioPagosPG, OutboxORM
from pagos.config.pulsar_config import settings
from sqlalchemy.orm import Session

async def despachador_outbox(repo: RepositorioPagosPG):
    """
    Implementa el patrón Outbox para garantizar la publicación confiable de eventos.
    
    Funcionamiento:
    1. Conecta con Pulsar y crea un productor para el tópico eventos-pago
    2. En un ciclo infinito:
        - Lee mensajes pendientes del outbox
        - Los publica a Pulsar
        - Marca como enviados en la misma transacción
    
    Args:
        repo: Repositorio PostgreSQL para acceder al outbox
    """
    # Inicializar cliente Pulsar y productor
    client = Client(settings.PULSAR_URL)
    producer = client.create_producer(
        topic=settings.TOPIC_PAGOS,
        batching_enabled=True,  # Habilita batch para mejor rendimiento
        block_if_queue_full=True  # Backpressure si Pulsar está sobrecargado
    )
    
    while True:
        with repo.SessionLocal() as session:
            # Obtener batch de mensajes pendientes
            outbox_items = session.query(OutboxORM).filter_by(status="PENDING").limit(settings.OUTBOX_BATCH_SIZE).all()
            
            for item in outbox_items:
                try:
                    # Publicar a Pulsar usando idPago como partition_key para ordenamiento
                    producer.send(item.payload.encode("utf-8"), partition_key=item.key)
                    # Marcar como enviado en la misma transacción
                    item.status = "SENT"
                    session.commit()
                except Exception as e:
                    print(f"Error publicando outbox {item.id}: {e}")
                    # No hace commit - el mensaje seguirá como PENDING para reintento
        
        # Esperar antes del siguiente batch
        await asyncio.sleep(2)
    
    client.close()

async def consumidor_referido(repo: RepositorioPagosPG):
    """
    Consumidor de eventos VentaReferidaConfirmada.
    
    Funcionamiento:
    1. Se suscribe al tópico eventos-referido-confirmado
    2. Al recibir un evento:
        - Si existe un pago en estado 'solicitado' → lo marca como 'completado'
        - Si no existe → crea un nuevo pago en estado 'completado'
    3. En ambos casos, publica un evento PagoCompletado vía outbox
    
    Args:
        repo: Repositorio PostgreSQL para acceder a pagos
    """
    # Inicializar cliente Pulsar y consumidor
    client = Client(settings.PULSAR_URL)  # version: '3.8'
    consumer = client.subscribe(
        topic=settings.TOPIC_REFERIDO_CONFIRMADO,
        subscription_name="pagos-svc",
        subscription_type="Shared"  # Permite escalar horizontalmente
    )
    
    while True:
        # Esperar nuevo mensaje con timeout
        msg = consumer.receive(timeout_millis=5000)
        if msg:
            # Procesar el evento recibido
            data = json.loads(msg.data())
            idEvento = data["idEvento"]
            idSocio = data["idSocio"]
            monto = data["monto"]
            fechaEvento = data["fechaEvento"]
            
            with repo.SessionLocal() as session:
                # Buscar si existe un pago solicitado para este evento
                pago_orm = session.query(repo.PagoORM).filter_by(idEvento=idEvento, estado="solicitado").first()
                
                if pago_orm:
                    # Actualizar pago existente
                    pago_orm.estado = "completado"
                    session.commit()
                    
                    # Preparar evento PagoCompletado
                    envelope = {
                        "meta": {
                            "event_id": pago_orm.idPago,
                            "schema_version": "v1",
                            "occurred_at": int(datetime.utcnow().timestamp()*1000),
                            "producer": settings.SERVICE_NAME,
                            "correlation_id": idEvento,
                            "causation_id": pago_orm.idPago
                        },
                        "key": pago_orm.idPago,
                        "state": {
                            "idPago": pago_orm.idPago,
                            "idEvento": pago_orm.idEvento,
                            "idSocio": pago_orm.idSocio,
                            "monto": float(pago_orm.monto),
                            "estado": "completado",
                            "fechaPago": pago_orm.fechaPago.isoformat()
                        }
                    }
                else:
                    # Crear nuevo pago en estado completado
                    from uuid import uuid4
                    idPago = str(uuid4())
                    pago_orm = repo.PagoORM(
                        idPago=idPago,
                        idEvento=idEvento,
                        idSocio=idSocio,
                        monto=monto,
                        estado="completado",
                        fechaPago=fechaEvento
                    )
                    session.add(pago_orm)
                    session.commit()
                    
                    # Preparar evento PagoCompletado
                    envelope = {
                        "meta": {
                            "event_id": idPago,
                            "schema_version": "v1",
                            "occurred_at": int(datetime.utcnow().timestamp()*1000),
                            "producer": settings.SERVICE_NAME,
                            "correlation_id": idEvento,
                            "causation_id": idPago
                        },
                        "key": idPago,
                        "state": {
                            "idPago": idPago,
                            "idEvento": idEvento,
                            "idSocio": idSocio,
                            "monto": monto,
                            "estado": "completado",
                            "fechaPago": fechaEvento
                        }
                    }
                
                # Agregar evento al outbox para publicación confiable
                repo.outbox_add(settings.TOPIC_PAGOS, pago_orm.idPago, json.dumps(envelope))
            
            # Confirmar procesamiento exitoso del mensaje
            consumer.acknowledge(msg)
    
    client.close()

async def main_worker():
    """
    Función principal que ejecuta los workers en paralelo.
    
    Inicia:
    1. Despachador de outbox para publicar eventos
    2. Consumidor de eventos de ventas referidas
    """
    # Inicializar repositorio compartido
    repo = RepositorioPagosPG(settings.DB_URL)
    
    # Ejecutar workers en paralelo usando asyncio
    await asyncio.gather(
        despachador_outbox(repo),
        consumidor_referido(repo)
    )

if __name__ == "__main__":
    # Punto de entrada cuando se ejecuta como script
    asyncio.run(main_worker())
