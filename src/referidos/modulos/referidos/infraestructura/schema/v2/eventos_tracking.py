"""
Esquemas de eventos para el microservicio de referidos
Eventos de tracking: EventoRegistrado (suscripción) y eventos de respuesta (publicación)
"""

from pulsar.schema import *
from dataclasses import dataclass
from typing import Optional
from seedwork.infraestructura.schema.v1.eventos import EventoIntegracion

class EventoRegistradoPayload(Record):
    """
    Payload para EventoRegistrado que se recibe del tópico eventos-tracking
    Estructura según especificación:
    {   
        "idEvento": "uuid",
        "tipoEvento": "venta_creada",
        "idReferido": "123e4567-e89b-12d3-a456-426614174004",
        "idSocio": "123e4567-e89b-12d3-a456-426614174004",
        "monto": 150.50,
        "estado": "pendiente",
        "fechaEvento": "2025-09-09T20:00:00Z"
    }
    """
    idEvento = String()
    tipoEvento = String()
    idReferido = String()
    idSocio = String()
    monto = Float()
    estado = String()
    fechaEvento = String()

class EventoRegistrado(EventoIntegracion):
    """
    Esquema para EventoRegistrado que se recibe del tópico comando-referido
    """
    idTransaction = String()
    data = EventoRegistradoPayload()

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
    Estructura según especificación:
    {
      "idEvento": "uuid"
    }
    """
    idEvento = String()

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