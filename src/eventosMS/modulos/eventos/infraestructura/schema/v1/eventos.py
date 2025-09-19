# Propósito: Definir el contrato público (esquema Avro/Pulsar) 
# para los eventos de integración que el servicio de pagos publicará.

from pulsar.schema import Record, String, Float
from seedwork.infraestructura.schema.v1.eventos import EventoIntegracion

class EventoRegistradoPayload(Record):
    idTransaction = String(required=False)
    idEvento = String()
    tipoEvento = String()
    idReferido = String()
    idSocio = String()
    monto = Float()
    estado = String()
    fechaEvento = String()

class EventoEventoRegistrado(EventoIntegracion):
    data = EventoRegistradoPayload()

class PagoCompletado(Record):
    """
    Evento publicado cuando un pago es completado exitosamente
    Tópico: eventos-pago
    """
    idPago = String()
    idEvento = String() 
    idSocio = String()
    monto = Float()
    estado = String()
    fechaPago = String()

class EventoCommandPayload(Record):
    """
    Payload para eventos de venta creada
    """
    tipoEvento = String()
    idEvento = String()
    idReferido = String()
    idSocio = String()
    monto = Float()
    fechaEvento = String()

class EventoCommand(EventoIntegracion):
    """
    Evento de comando para iniciar o cancelar transacciones
    Incluye información de venta creada
    Tópico: comandos-transaccion
    """
    comando = String()  # "Iniciar" o "Cancelar"
    idTransaction = String(required=False)  # Campo opcional
    data = EventoCommandPayload()