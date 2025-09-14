# Propósito: Definir los objetos valor que encapsulan conceptos y reglas 
# inmutables del dominio de referidos.

from __future__ import annotations
from dataclasses import dataclass
from seedwork.dominio.objetos_valor import ObjetoValor
import uuid # Importa uuid

@dataclass(frozen=True)
class Monto(ObjetoValor):
    valor: float
    moneda: str