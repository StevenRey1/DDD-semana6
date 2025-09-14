from datetime import datetime
from typing import Any

class PagoSolicitado:
    def __init__(self, idPago: str, idEvento: str, idSocio: str, monto: float, fecha: datetime):
        self.idPago = idPago
        self.idEvento = idEvento
        self.idSocio = idSocio
        self.monto = monto
        self.fecha = fecha
    @staticmethod
    def emit(pago):
        # Aquí se podría agregar lógica de publicación de eventos internos
        pass

class PagoCompletado(PagoSolicitado):
    @staticmethod
    def emit(pago):
        pass

class PagoRechazado(PagoSolicitado):
    @staticmethod
    def emit(pago):
        pass
