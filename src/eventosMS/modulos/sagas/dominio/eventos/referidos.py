from typing import Optional
from eventosMS.seedwork.dominio.eventos import (EventoDominio)
from dataclasses import dataclass, field

@dataclass 
class ReferidoProcesado(EventoDominio):
    idTransaction: str = None
    idEvento: str = None
    idSocio : str = None
    monto: float = None
    estado : str = None
    fechaEvento : str = None
