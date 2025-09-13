from __future__ import annotations
from dataclasses import dataclass
from seedwork.dominio.eventos import (EventoDominio)
import uuid
from datetime import datetime

@dataclass
class ReferidoCreado(EventoDominio):
    idSocio: uuid.UUID = None
    idReferido: uuid.UUID = None
    idEvento: uuid.UUID = None
    monto: float = None
    estado: str = None
    fechaEvento: datetime = None
    tipoEvento: str = None
    fecha_creacion: datetime = None

@dataclass
class ReferidoConfirmado(EventoDominio):
    referido_id: uuid.UUID = None
    id_afiliado: uuid.UUID = None
    tipo_accion: str = None
    detalle_accion: str = None
    fecha_creacion: datetime = None
