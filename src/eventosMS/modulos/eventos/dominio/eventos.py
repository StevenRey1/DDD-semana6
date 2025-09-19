"""
Eventos de Dominio del módulo de Eventos
"""
from __future__ import annotations
from dataclasses import dataclass, field
from seedwork.dominio.eventos import EventoDominio
from datetime import datetime
from uuid import UUID


@dataclass
class EventoRegistrado(EventoDominio):
    """
    Evento que se dispara cuando se crea un nuevo evento en el sistema
    """
    evento_id: UUID = field(default=None)
    tipo_evento: str = field(default="")
    id_referido: UUID = field(default=None)
    id_socio: UUID = field(default=None)
    monto: float = field(default=0.0)
    ganancia: float = field(default=0.0)
    estado: str = field(default="pendiente")
    fecha_evento: datetime = field(default_factory=datetime.now)
    comando: str = field(default=None)  # "Iniciar" | "Cancelar"
    id_transaction: str = field(default=None)

    def nombre_evento(self) -> str:
        return "eventos.eventos-tracking"


@dataclass
class EventoPagoActualizado(EventoDominio):
    """
    Evento que se dispara cuando se actualiza un evento con información de pago
    """
    evento_id: UUID = field(default=None)
    id_pago: str = field(default="")
    estado_anterior: str = field(default="")
    estado_nuevo: str = field(default="")
    ganancia_anterior: float = field(default=0.0)
    ganancia_nueva: float = field(default=0.0)
    fecha_pago: str = field(default="")
    monto_pago: float = field(default=0.0)

    def nombre_evento(self) -> str:
        return "eventos.pago-actualizado"
