"""
Esquemas de eventos para notificaciones desde el microservicio de referidos
"""

from pulsar.schema import *

class VentaReferidaConfirmada(Record):
    """
    Evento recibido cuando una venta referida es confirmada
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
    Evento recibido cuando una venta referida es rechazada
    Tópico: eventos-referido-rechazado
    Estructura según especificación:
    {
      "idEvento": "uuid",
      "idSocio": "uuid",
      "monto": 123.45, 
      "razon": "Motivo del rechazo",
      "fechaEvento": "2025-09-09T20:00:00Z"
    }
    """
    idEvento = String()
    idSocio = String()
    monto = Float()
    razon = String()
    fechaEvento = String()