
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


class ReferidoCommandPayload(Record):
    """
    Payload para referido
    """
    tipoEvento = String()
    idEvento = String()
    idReferido = String()
    idSocio = String()
    monto = Float()
    fechaEvento = String()
    estadoEvento = String()

class ReferidoProcesado(EventoIntegracion):
    """
    Evento de comando para iniciar o cancelar transacciones
    Incluye información de venta creada
    Tópico: comandos-transaccion
    """
    idTransaction = String(required=False)
    data = ReferidoCommandPayload()


class PagoProcesado(Record):
    
        idTransaction = String()  # Opcional en el contrato, obligatorio en Avro
        idPago = String()
        idEvento = String() 
        idSocio = String()
        monto = Float()
        estado = String()
        fechaEvento = String()