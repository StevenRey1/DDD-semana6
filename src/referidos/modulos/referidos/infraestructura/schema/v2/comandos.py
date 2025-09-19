# Propósito: Definir el esquema para los comandos que este servicio podría 
# consumir de forma asíncrona.

from pulsar.schema import *
from seedwork.infraestructura.schema.v1.comandos import ComandoIntegracion

class ComandoCrearReferidoPayload(Record):
    id_referido = String()

class ComandoCrearReferido(ComandoIntegracion):
    data = ComandoCrearReferidoPayload()

class ComandoConfirmarReferidoPayload(Record):
    id_referido = String()

class ComandoConfirmarReferido(ComandoIntegracion):
    data = ComandoConfirmarReferidoPayload()