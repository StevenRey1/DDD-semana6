# Propósito: Definir los objetos valor que encapsulan conceptos y reglas 
# inmutables del dominio de referidos.

from __future__ import annotations
from dataclasses import dataclass
from seedwork.dominio.objetos_valor import ObjetoValor
from enum import Enum
import uuid # Importa uuid

@dataclass(frozen=True)
class Monto(ObjetoValor):
    valor: float
    moneda: str


class TipoAccion(str, Enum):
    REGISTRO = "Registro"
    VENTA = "VENTA"
    OTRO = "Otro"

class TipoEvento(str, Enum):
    VENTA = "venta_creada"

class EstadoReferido(str, Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    RECHAZADO = "RECHAZADO"