# Propósito: Definir el esquema para los comandos que este servicio podría 
# consumir de forma asíncrona.

from pulsar.schema import *
from seedwork.infraestructura.schema.v1.comandos import ComandoIntegracion

class ComandoCrearEventoPayload(ComandoIntegracion):
    id_evento = String()
    tipo_evento = String()
    id_referido = String()
    id_socio = String()
    monto = Float()
    estado = String()
    fecha_evento = String()

class ComandoCrearEvento(ComandoIntegracion):
    data = ComandoCrearEventoPayload()