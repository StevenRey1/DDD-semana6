# Propósito: Definir el contrato público (esquema Avro/Pulsar) 

from pulsar.schema import *
from seedwork.infraestructura.schema.v1.eventos import EventoIntegracion

class EventoReferidoCreadoPayload(Record):
    referido_id = String()  # ID del referido generado
    afiliado_id = String()  # ID del usuario que generó el referido
    tipo_accion = String()  # Tipo de acción que generó el referido (e.g., 'registro', 'compra')
    fecha_accion = Long()  # Timestamp de la acción
    detalle_accion = String()  # Detalles adicionales sobre la acción

class EventoReferidoCreado(EventoIntegracion):
    data = EventoReferidoCreadoPayload()  # Datos relevantes del referido

class EventoReferidoConfirmadoPayload(Record):
    venta_id = String()  # ID de la venta realizada
    afiliado_id = String()  # ID del afiliado que refirió al usuario
    referido_id = String()  # ID del referido asociado a la venta
    valor_venta = Float()  # Monto total de la venta
    fecha_venta = Long()  # Timestamp de la venta

class EventoReferidoConfirmado(EventoIntegracion):
    data = EventoReferidoConfirmadoPayload()  # Datos relevantes de la venta del referido