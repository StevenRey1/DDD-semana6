# Propósito: Definir el contrato público (esquema Avro/Pulsar) 
# para los eventos de integración que el servicio de pagos publicará.

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

class EventoEventoRegistrado(EventoIntegracion):
    data = EventoRegistradoPayload()