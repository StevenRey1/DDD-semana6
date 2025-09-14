"""
Schema para eventos de referidos confirmados/rechazados
Copiado del microservicio de referidos para compatibilidad de Avro
"""

from pulsar.schema import *


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


class VentaReferidaRechazada(Record):
    """
    Evento publicado cuando una venta referida es rechazada
    Tópico: eventos-referido-rechazado
    """
    idEvento = String()
    idSocio = String()
    razon = String()
    fechaEvento = String()