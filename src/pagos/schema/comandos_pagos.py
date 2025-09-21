"""
Schemas Avro para comandos que recibe el microservicio de pagos
Según especificación actualizada
"""

from pulsar.schema import Record, String, Float

class PagoCommandData(Record):
    """Datos del comando de pago"""
    idEvento = String()
    idSocio = String()
    monto = Float()
    fechaEvento = String()

class PagoCommandMessage(Record):
    """
    Comando de pago que llega vía tópico comando-pago
    Según especificación del contrato
    """
    comando = String()  
    idTransaction = String()  # Opcional pero requerido en Avro
    data = PagoCommandData()

