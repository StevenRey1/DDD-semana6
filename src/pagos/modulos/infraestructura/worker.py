import asyncio
import json
from pulsar import Client
from .repositorio_postgresql import RepositorioPagosPG, OutboxORM
from ..config.pulsar_config import settings
from sqlalchemy.orm import Session

async def despachador_outbox(repo: RepositorioPagosPG):
    client = Client(settings.PULSAR_URL)
    producer = client.create_producer(topic=settings.TOPIC_PAGOS, batching_enabled=True, block_if_queue_full=True)
    while True:
        with repo.SessionLocal() as session:
            outbox_items = session.query(OutboxORM).filter_by(status="PENDING").limit(settings.OUTBOX_BATCH_SIZE).all()
            for item in outbox_items:
                try:
                    producer.send(item.payload.encode("utf-8"), partition_key=item.key)
                    item.status = "SENT"
                    session.commit()
                except Exception as e:
                    print(f"Error publicando outbox {item.id}: {e}")
        await asyncio.sleep(2)
    client.close()

async def consumidor_referido(repo: RepositorioPagosPG):
    client = Client(settings.PULSAR_URL)
    consumer = client.subscribe(topic=settings.TOPIC_REFERIDO_CONFIRMADO, subscription_name="pagos-svc", subscription_type="Shared")
    while True:
        msg = consumer.receive(timeout_millis=5000)
        if msg:
            data = json.loads(msg.data())
            idEvento = data["idEvento"]
            idSocio = data["idSocio"]
            monto = data["monto"]
            fechaEvento = data["fechaEvento"]
            with repo.SessionLocal() as session:
                pago_orm = session.query(repo.PagoORM).filter_by(idEvento=idEvento, estado="solicitado").first()
                if pago_orm:
                    pago_orm.estado = "completado"
                    session.commit()
                    # Envelope y outbox
                    envelope = {
                        "meta": {"event_id": pago_orm.idPago, "schema_version": "v1", "occurred_at": int(datetime.utcnow().timestamp()*1000), "producer": settings.SERVICE_NAME, "correlation_id": idEvento, "causation_id": pago_orm.idPago},
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
                    repo.outbox_add(settings.TOPIC_PAGOS, pago_orm.idPago, json.dumps(envelope))
                else:
                    # Crear pago completado
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
                    envelope = {
                        "meta": {"event_id": idPago, "schema_version": "v1", "occurred_at": int(datetime.utcnow().timestamp()*1000), "producer": settings.SERVICE_NAME, "correlation_id": idEvento, "causation_id": idPago},
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
                    repo.outbox_add(settings.TOPIC_PAGOS, idPago, json.dumps(envelope))
            consumer.acknowledge(msg)
    client.close()

async def main_worker():
    from ..config.pulsar_config import settings
    repo = RepositorioPagosPG(settings.DB_URL)
    await asyncio.gather(
        despachador_outbox(repo),
        consumidor_referido(repo)
    )

if __name__ == "__main__":
    asyncio.run(main_worker())
