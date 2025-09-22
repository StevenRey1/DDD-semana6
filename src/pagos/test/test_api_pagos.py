import pytest
from fastapi.testclient import TestClient
from main import app
from uuid import uuid4

client = TestClient(app)

def test_post_pagos_iniciar():
    """Test comando Iniciar según especificación"""
    data = {
        "comando": "Iniciar",
        "idTransaction": str(uuid4()),
        "data": {
            "idEvento": str(uuid4()),
            "idSocio": str(uuid4()),
            "monto": 123.45,
            "fechaEvento": "2025-09-09T20:00:00Z"
        }
    }
    resp = client.post("/pagos", json=data)
    assert resp.status_code == 202
    assert "message" in resp.json()

def test_post_pagos_cancelar():
    """Test comando Cancelar según especificación"""
    data = {
        "comando": "Cancelar", 
        "idTransaction": str(uuid4()),
        "data": {
            "idEvento": str(uuid4()),
            "idSocio": str(uuid4()),
            "monto": 123.45,
            "fechaEvento": "2025-09-09T20:00:00Z"
        }
    }
    resp = client.post("/pagos", json=data)
    assert resp.status_code == 202
    assert "message" in resp.json()

def test_get_pagos_estado():
    """Test consulta de estado según especificación"""
    fake_pago_id = str(uuid4())
    resp = client.get(f"/pagos/{fake_pago_id}")
    # Esperamos 404 para ID inexistente
    assert resp.status_code == 404

def test_health_check():
    """Test health check endpoint"""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    assert resp.json()["service"] == "pagos"
