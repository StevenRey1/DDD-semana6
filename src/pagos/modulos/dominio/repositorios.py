from typing import Optional
from .entidades import Pago

class RepoPagos:
    def by_id(self, idPago: str) -> Optional[Pago]:
        raise NotImplementedError
    def guardar(self, pago: Pago) -> None:
        raise NotImplementedError
