# Propósito: Definir reglas de negocio de forma explícita, 
# haciéndolas reutilizables y fáciles de validar.

"""Reglas de negocio del dominio de Pagos"""

from seedwork.dominio.reglas import ReglaNegocio

class MontoDebeSerPositivo(ReglaNegocio):
    monto: float

    def __init__(self, monto: float, mensaje='El monto total del pago debe ser un valor positivo'):
        super().__init__(mensaje)
        self.monto = monto

    def es_valido(self) -> bool:
        return self.monto > 0