from __future__ import annotations
from dataclasses import dataclass
from seedwork.dominio.eventos import (EventoDominio)
import uuid
from datetime import datetime

@dataclass
class VentaReferidaConfirmada(EventoDominio):
    id_evento: uuid.UUID = None
    id_socio: uuid.UUID = None
    monto: float = None
    fecha_evento: datetime = None

@dataclass
class VentaReferidaRechazada(EventoDominio):
    id_evento: uuid.UUID = None