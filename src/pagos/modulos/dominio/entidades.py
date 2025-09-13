from datetime import datetime
from typing import Optional
from .eventos import PagoSolicitado, PagoCompletado, PagoRechazado

class Pago:
    """
    Agregado raíz para pagos
    """
    def __init__(self, idPago: str, idEvento: str, idSocio: str, monto: float, estado: str, fechaPago: datetime):
        self.idPago = idPago
        self.idEvento = idEvento
        self.idSocio = idSocio
        self.monto = monto
        self.estado = estado
        self.fechaPago = fechaPago

    @classmethod
    def solicitar(cls, idEvento: str, idSocio: str, monto: float) -> "Pago":
        from uuid import uuid4
        pago = cls(
            idPago=str(uuid4()),
            idEvento=idEvento,
            idSocio=idSocio,
            monto=monto,
            estado="solicitado",
            fechaPago=datetime.utcnow()
        )
        PagoSolicitado.emit(pago)
        return pago

    def completar(self) -> "Pago":
        self.estado = "completado"
        self.fechaPago = datetime.utcnow()
        PagoCompletado.emit(self)
        return self

    def rechazar(self) -> "Pago":
        self.estado = "rechazado"
        self.fechaPago = datetime.utcnow()
        PagoRechazado.emit(self)
        return self
