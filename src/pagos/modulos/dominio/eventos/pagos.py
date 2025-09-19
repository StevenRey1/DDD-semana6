from datetime import datetime
from typing import Optional

class PagoProcesado:
    """
    Evento que se publica al tópico eventos-pago según especificación.
    Este es el único evento que necesitamos según la nueva especificación.
    """
    def __init__(self, idTransaction: Optional[str], idPago: str, idEvento: str, idSocio: str, monto: float, estado_pago: str, fechaPago: datetime):
        self.idTransaction = idTransaction
        self.idPago = idPago
        self.idEvento = idEvento
        self.idSocio = idSocio
        self.monto = monto
        self.estado_pago = estado_pago  # "solicitado" | "completado" | "rechazado"
        self.fechaPago = fechaPago

    @classmethod
    def from_pago(cls, pago) -> "PagoProcesado":
        """Crear evento desde entidad Pago"""
        return cls(
            idTransaction=pago.idTransaction,
            idPago=pago.idPago,
            idEvento=pago.idEvento,
            idSocio=pago.idSocio,
            monto=pago.monto,
            estado_pago=pago.estado,
            fechaPago=pago.fechaPago
        )

    def to_dict(self) -> dict:
        """Convertir a diccionario para publicación"""
        return {
            "idTransaction": self.idTransaction,
            "idPago": self.idPago,
            "idEvento": self.idEvento,
            "idSocio": self.idSocio,
            "monto": self.monto,
            "estado_pago": self.estado_pago,
            "fechaPago": self.fechaPago.isoformat() if self.fechaPago else None
        }
