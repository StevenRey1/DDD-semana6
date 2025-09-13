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