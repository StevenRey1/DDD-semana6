"""
Clases base simples para cuando no se puede importar desde seedwork
"""

from abc import ABC
from typing import List
from datetime import datetime


class EventoDominioSimple:
    """Evento de dominio base simple"""
    
    def __init__(self):
        self.fecha_evento = datetime.now()
    
    def to_dict(self):
        """Convierte el evento a diccionario"""
        return {
            "tipo_evento": self.__class__.__name__,
            "fecha_evento": self.fecha_evento.isoformat()
        }


class AgregacionRaizSimple(ABC):
    """Agregación raíz base simple"""
    
    def __init__(self):
        self.eventos: List[EventoDominioSimple] = []
    
    def agregar_evento(self, evento: EventoDominioSimple):
        """Agrega un evento de dominio"""
        self.eventos.append(evento)
    
    def limpiar_eventos(self):
        """Limpia los eventos después de publicarlos"""
        self.eventos.clear()


class ObjetoValorSimple:
    """Objeto valor base simple"""
    
    def __init__(self, valor):
        self.valor = valor
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.valor == other.valor
    
    def __hash__(self):
        return hash(self.valor)
    
    def __str__(self):
        return str(self.valor)
