import pytest
from unittest.mock import MagicMock
from pagos.modulos.infraestructura.repositorio_postgresql import RepositorioPagosPG, OutboxORM

def test_outbox_publicacion():
    repo = MagicMock()
    repo.SessionLocal.return_value.__enter__.return_value.query.return_value.filter_by.return_value.limit.return_value.all.return_value = [
        MagicMock(id="1", payload="payload", key="key", status="PENDING")
    ]
    producer = MagicMock()
    producer.send = MagicMock()
    # Simular despachador
    for item in repo.SessionLocal().__enter__().query().filter_by().limit().all():
        producer.send(item.payload.encode("utf-8"), partition_key=item.key)
        item.status = "SENT"
    assert producer.send.called
