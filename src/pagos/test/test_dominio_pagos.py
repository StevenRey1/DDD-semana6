import pytest
from pagos.modulos.dominio.entidades import Pago

def test_pago_solicitar():
    pago = Pago.solicitar("evento1", "socio1", 100.0)
    assert pago.estado == "solicitado"
    assert pago.monto == 100.0

def test_pago_completar():
    pago = Pago.solicitar("evento2", "socio2", 200.0)
    pago.completar()
    assert pago.estado == "completado"
    assert pago.fechaPago is not None
