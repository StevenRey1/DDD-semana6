# Propósito: Definir el contrato público (esquema Avro/Pulsar) 
# para los eventos de integración que el servicio de pagos publicará.

from pulsar.schema import *
from seedwork.infraestructura.schema.v1.eventos import EventoIntegracion

class EventoRegistradoPayload(Record):
    id_evento = String()
    tipo_evento = String()
    id_referido = String()
    id_socio = String()
    monto = Float()
    estado = String()
    fecha_evento = String()

class EventoEventoRegistrado(EventoIntegracion):
    data = EventoRegistradoPayload()