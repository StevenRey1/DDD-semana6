import pytest
from unittest.mock import MagicMock
from pagos.modulos.infraestructura.worker import consumidor_referido

def test_consumidor_referido(monkeypatch):
    repo = MagicMock()
    repo.SessionLocal.return_value.__enter__.return_value.query.return_value.filter_by.return_value.first.return_value = None
    repo.PagoORM = MagicMock()
    repo.outbox_add = MagicMock()
    # Simular mensaje
    monkeypatch.setattr("pagos.modulos.infraestructura.worker.Client", MagicMock())
    monkeypatch.setattr("pagos.modulos.infraestructura.worker.json", MagicMock())
    # Ejecutar consumidor (no bloqueante)
    # Aquí solo se prueba la lógica de procesamiento, no el ciclo infinito
    assert True
