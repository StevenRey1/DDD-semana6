from typing import Optional
from ..dominio.entidades import Pago
from ..dominio.repositorios import RepoPagos
from ..aplicacion.dto import PagoIntegracion

class ServicioPagos:
    def __init__(self, repo: RepoPagos):
        self.repo = repo

    def solicitar_pago(self, idEvento: str, idSocio: str, monto: float) -> Pago:
        pago = Pago.solicitar(idEvento, idSocio, monto)
        self.repo.guardar(pago)
        return pago

    def obtener_pago(self, idPago: str) -> Optional[Pago]:
        return self.repo.by_id(idPago)
