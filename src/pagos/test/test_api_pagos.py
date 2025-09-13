import pytest
from fastapi.testclient import TestClient
from pagos.main import app

client = TestClient(app)

def test_post_pagos():
    data = {
        "idEvento": "evento1",
        "idSocio": "socio1",
        "monto": 123.45,
        "fechaEvento": "2025-09-09T20:00:00Z"
    }
    resp = client.post("/pagos", json=data)
    assert resp.status_code == 202
    assert "operation_id" in resp.json()

def test_get_pagos():
    # Primero crear
    data = {
        "idEvento": "evento2",
        "idSocio": "socio2",
        "monto": 200.0,
        "fechaEvento": "2025-09-09T20:00:00Z"
    }
    resp = client.post("/pagos", json=data)
    idPago = resp.json()["operation_id"]
    resp2 = client.get(f"/pagos/{idPago}")
    assert resp2.status_code == 200
    assert resp2.json()["idPago"] == idPago
