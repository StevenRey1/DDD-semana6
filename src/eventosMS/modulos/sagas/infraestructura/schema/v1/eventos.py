
from attr import dataclass
from pulsar.schema import *
from eventosMS.seedwork.infraestructura.schema.v1.eventos import EventoIntegracion

class IniciarSagaPagoPayload(Record):
    idTransaction = String(required=False)
    idEvento = String()
    tipoEvento = String()
    idReferido = String()
    idSocio = String()
    monto = Float()
    estado = String()
    fechaEvento = String()
    
class IniciarSagaPago(EventoIntegracion):
    data = IniciarSagaPagoPayload()