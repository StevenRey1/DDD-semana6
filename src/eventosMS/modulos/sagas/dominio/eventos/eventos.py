
from typing import Optional
from eventosMS.seedwork.dominio.eventos import (EventoDominio)
from dataclasses import dataclass, field
 
@dataclass    
class EventoRegistradoPayload():
    idTransaction: str = None
    idEvento: str = None
    tipoEvento : str = None
    idReferido : str = None
    idSocio : str = None
    monto: float = None
    estado : str = None
    fechaEvento : str = None
    
@dataclass 
class EventoProcesado(EventoDominio):
    data = EventoRegistradoPayload()

@dataclass
class CrearEvento(EventoDominio):
    id_socio: str = None
    id_referido: str = None
    monto: float = None
    fecha_evento: str = None
    tipo: str = None
    comando: Optional[str] = None  # "Iniciar" | "Cancelar"
    id_transaction: Optional[str] = None  # ID de negocio (transacción de pago/evento)
    correlation_id: Optional[str] = None  # ID técnico para trazar la saga (separado de id_transaction)
    
@dataclass
class EventoError(EventoDominio):
    ...

@dataclass
class EventoCompensacion(EventoDominio):
    ...
