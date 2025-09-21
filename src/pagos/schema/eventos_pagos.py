"""
Schema Avro para el evento que publica el microservicio de pagos
Según especificación actualizada
"""

from pulsar.schema import Record, String, Float

class ProcesarPago(Record):
  
    idTransaction = String()  # Opcional en el contrato, obligatorio en Avro
    comando = String()
    idEvento = String() 
    idSocio = String()
    monto = Float()
    fechaEvento = String()