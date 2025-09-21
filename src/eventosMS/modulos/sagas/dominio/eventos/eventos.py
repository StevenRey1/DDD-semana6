
from typing import Optional
from eventosMS.seedwork.dominio.eventos import (EventoDominio)
from dataclasses import dataclass, field

@dataclass 
class EventoRegistrado(EventoDominio):
    idTransaction: str = None
    idEvento: str = None
    tipoEvento : str = None
    idReferido : str = None
    idSocio : str = None
    monto: float = None
    estado : str = None
    fechaEvento : str = None
    comando: str = None

@dataclass
class CrearEvento(EventoDominio):
    id_socio: str = None
    id_referido: str = None
    monto: float = None
    fecha_evento: str = None
    tipo: str = None
    comando: Optional[str] = None  # "Iniciar" | "Cancelar"
    id_transaction: Optional[str] = None
    
@dataclass
class EventoError(EventoDominio):
    ...

@dataclass
class EventoCompensacion(EventoDominio):
    ...