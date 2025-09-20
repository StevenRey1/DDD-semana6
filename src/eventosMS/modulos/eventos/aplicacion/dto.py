"""
DTOs del módulo de Eventos
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class EventoDTO:
    """DTO para transferencia de datos de eventos"""
    tipo: str
    id_socio: UUID
    id_referido: UUID
    monto: float
    fecha_evento: str
    comando: Optional[str] = None  # "Iniciar" | "Cancelar"
    id_transaction: Optional[str] = None
    id_evento: Optional[str] = None


@dataclass(frozen=True)
class ActualizarEventoPagoDTO:
    """DTO para actualizar un evento con información de pago completado"""
    id_evento: str
    id_pago: str
    estado_pago: str
    ganancia: float
    fecha_pago: str
    monto_pago: float


@dataclass(frozen=True)
class EventoTrackingDTO:
    """DTO para eventos de tracking"""
    id_transaction: Optional[str]
    id_evento: str
    tipo_evento: str
    id_referido: str
    id_socio: str
    monto: float
    estado_evento: str  # "pendiente" | "rechazado" | "pago_completado"
    fecha_evento: str