"""
Schemas Avro para eventos que publica el microservicio de pagos
"""

from pulsar.schema import Record, String, Float

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

class PagoRechazado(Record):
    """
    Evento publicado cuando un pago es rechazado
    Tópico: eventos-pago  
    """
    idPago = String()
    idEvento = String()
    idSocio = String() 
    monto = Float()
    estado = String()
    fechaPago = String()
    motivo = String()