from __future__ import annotations
from dataclasses import dataclass, field
from eventosMS.seedwork.dominio.eventos import EventoDominio
from datetime import datetime

@dataclass
class PagoProcesado(EventoDominio):
    
    idTransaction : str = None
    idPago : str = None
    idEvento : str = None
    idSocio : str = None
    monto : float = None
    estado : str = None
    fechaEvento : str = None