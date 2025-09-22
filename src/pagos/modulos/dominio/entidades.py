from datetime import datetime
from typing import Optional
from .eventos import PagoProcesado

class Pago:
    """
    Agregado raíz para pagos según especificación
    """
    def __init__(self, idPago: str, idEvento: str, idSocio: str, monto: float, estado: str, fechaPago: datetime, idTransaction: Optional[str] = None):
        self.idPago = idPago
        self.idEvento = idEvento
        self.idSocio = idSocio
        self.monto = monto
        self.estado = estado  # "solicitado" | "completado" | "rechazado"
        self.fechaPago = fechaPago
        self.idTransaction = idTransaction

    @classmethod
    def solicitar(cls, idEvento: str, idSocio: str, monto: float, idTransaction: Optional[str] = None) -> "Pago":
        from uuid import uuid4
        pago = cls(
            idPago=str(uuid4()),
            idEvento=idEvento,
            idSocio=idSocio,
            monto=monto,
            estado="solicitado",
            fechaPago=datetime.utcnow(),
            idTransaction=idTransaction
        )
        return pago

    def completar(self) -> "Pago":
        self.estado = "completado"
        self.fechaPago = datetime.utcnow()
        return self

    def rechazar(self) -> "Pago":
        self.estado = "rechazado"
        self.fechaPago = datetime.utcnow()
        return self
