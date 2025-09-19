"""
Schemas Avro para eventos que publica el microservicio de pagos
Según especificación actualizada
"""

from pulsar.schema import Record, String, Float

class PagoProcesado(Record):
    """
    Evento unificado publicado cuando un pago es procesado.
    Incluye estados: solicitado | completado | rechazado
    Tópico: eventos-pago
    """
    idTransaction = String()  # Opcional en el contrato, obligatorio en Avro
    idPago = String()
    idEvento = String() 
    idSocio = String()
    monto = Float()
    estado_pago = String()  # "solicitado | completado | rechazado"
    fechaPago = String()

# Mantener eventos legacy por compatibilidad (deprecados)
class PagoCompletado(Record):
    """DEPRECADO: Usar PagoProcesado"""
    idPago = String()
    idEvento = String() 
    idSocio = String()
    monto = Float()
    estado = String()
    fechaPago = String()

class PagoRechazado(Record):
    """DEPRECADO: Usar PagoProcesado"""
    idPago = String()
    idEvento = String()
    idSocio = String() 
    monto = Float()
    estado = String()
    fechaPago = String()
    motivo = String()