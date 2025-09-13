"""
Objetos de Valor del dominio de Eventos
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from seedwork.dominio.objetos_valor import ObjetoValor
from datetime import datetime
from typing import Dict, Any, Optional


class TipoEvento(Enum):
    """Enumeración de tipos de eventos soportados"""
    VENTA_CREADA = "venta_creada"

    @property
    def valor(self) -> str:
        return self.value
