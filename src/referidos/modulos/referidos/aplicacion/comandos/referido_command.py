from dataclasses import dataclass, field
from seedwork.aplicacion.comandos import Comando
from seedwork.aplicacion.dto import DTO
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class ReferidoCommandDTO(DTO):
    idEvento: str
    tipoEvento: str
    idReferido: str
    monto: float
    estado_evento: str
    fechaEvento: datetime

@dataclass(frozen=True)
class ReferidoCommand(Comando):
    comando: str
    idSocio: str
    data: ReferidoCommandDTO