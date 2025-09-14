from pulsar.schema import *
from seedwork.infraestructura.schema.v1.eventos import EventoIntegracion

class EventoRegistradoPayload(Record):
    idEvento = String()
    tipoEvento = String()
    idReferido = String()
    idSocio = String()
    monto = Float()
    estado = String()
    fechaEvento = String()

class EventoRegistrado(EventoIntegracion):
    data = EventoRegistradoPayload()

class VentaReferidaConfirmadaPayload(Record):
    id_evento = String()
    id_socio = String()
    monto = Float()
    fecha_evento = String()

class VentaReferidaConfirmada(EventoIntegracion):
    data = VentaReferidaConfirmadaPayload()

class VentaReferidaRechazadaPayload(Record):
    id_evento = String()

class VentaReferidaRechazada(EventoIntegracion):
    data = VentaReferidaRechazadaPayload()