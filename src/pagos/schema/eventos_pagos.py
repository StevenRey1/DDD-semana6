"""
Schema Avro para el evento que publica el microservicio de pagos
Según especificación actualizada
"""

from pulsar.schema import Record, String, Float

class PagoProcesado(Record):
    """
    Evento publicado cuando un pago es procesado.
    Estados: solicitado | completado | rechazado
    Tópico: eventos-pago
    Estructura según especificación (camelCase):
    {
      "idTransaction": "222e4567-e89b-12d3-a456-98546546544",
      "idPago": "uuid",
      "idEvento": "uuid",
      "idSocio": "uuid", 
      "monto": 123.45,
      "estadoPago": "solicitado | completado | rechazado",
      "fechaPago": "2025-09-09T20:00:00Z"
    }
    """
    idTransaction = String()  # Opcional en el contrato, obligatorio en Avro
    idPago = String()
    idEvento = String() 
    idSocio = String()
    monto = Float()
    estadoPago = String()  # "solicitado | completado | rechazado"
    fechaPago = String()