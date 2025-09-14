"""
Schema para eventos de VentaReferidaConfirmada
Copiado del microservicio de referidos para compatibilidad de Avro
"""

from pulsar.schema import Record, String, Float

class VentaReferidaConfirmada(Record):
    """
    Evento publicado cuando una venta referida es confirmada
    Tópico: eventos-referido-confirmado
    Estructura según especificación:
    {
      "idEvento": "uuid",
      "idSocio": "uuid", 
      "monto": 123.45,
      "fechaEvento": "2025-09-09T20:00:00Z"
    }
    """
    idEvento = String()
    idSocio = String()
    monto = Float()
    fechaEvento = String()