from pulsar.schema import Record, String, Float
from seedwork.infraestructura.schema.v1.eventos import EventoIntegracion



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
    # comando = String()
    idTransaction = String(required=False)
    data = ReferidoCommandPayload()

class ProcesarPago(EventoIntegracion):

    comando = String()
    idTransaction = String()  # Opcional en el contrato, obligatorio en Avro
    idEvento = String() 
    idSocio = String()
    monto = Float()
    fechaEvento = String()