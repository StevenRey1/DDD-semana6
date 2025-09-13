from dataclasses import dataclass
from typing import List
import re

# Import condicional de seedwork
try:
    from ....seedwork.dominio.objetos_valor import ObjetoValor
except ImportError:
    # Fallback cuando se ejecuta directamente
    from .base_simple import ObjetoValorSimple as ObjetoValor


@dataclass(frozen=True)
class TipoNotificacion(ObjetoValor):
    """Objeto valor para el tipo de notificación"""
    valor: str
    
    TIPOS_VALIDOS = [
        "bienvenida",
        "confirmacion", 
        "alerta",
        "promocional",
        "transaccional",
        "informativa",
        "recompensa",
        "recordatorio",
        "sistema"
    ]
    
    def __post_init__(self):
        if not self.valor:
            raise ValueError("El tipo de notificación es requerido")
        
        if self.valor not in self.TIPOS_VALIDOS:
            raise ValueError(f"Tipo de notificación inválido: {self.valor}. Tipos válidos: {self.TIPOS_VALIDOS}")


@dataclass(frozen=True)
class CanalNotificacion(ObjetoValor):
    """Objeto valor para el canal de notificación"""
    valor: str
    
    CANALES_VALIDOS = [
        "email",
        "sms", 
        "push",
        "whatsapp",
        "slack",
        "teams"
    ]
    
    def __post_init__(self):
        if not self.valor:
            raise ValueError("El canal de notificación es requerido")
        
        if self.valor not in self.CANALES_VALIDOS:
            raise ValueError(f"Canal de notificación inválido: {self.valor}. Canales válidos: {self.CANALES_VALIDOS}")


@dataclass(frozen=True)
class EstadoNotificacion(ObjetoValor):
    """Objeto valor para el estado de la notificación"""
    valor: str
    
    ESTADOS_VALIDOS = [
        "pendiente",
        "enviada",
        "fallida",
        "cancelada"
    ]
    
    def __post_init__(self):
        if not self.valor:
            raise ValueError("El estado de notificación es requerido")
        
        if self.valor not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado de notificación inválido: {self.valor}. Estados válidos: {self.ESTADOS_VALIDOS}")
    
    def es_final(self) -> bool:
        """Determina si el estado es final (no puede cambiar)"""
        return self.valor in ["enviada", "cancelada"]


@dataclass(frozen=True)
class Email(ObjetoValor):
    """Objeto valor para email"""
    direccion: str
    
    def __post_init__(self):
        if not self.direccion:
            raise ValueError("La dirección de email es requerida")
        
        if "@" not in self.direccion or "." not in self.direccion.split("@")[-1]:
            raise ValueError("Formato de email inválido")


@dataclass(frozen=True)
class Telefono(ObjetoValor):
    """Objeto valor para número de teléfono"""
    numero: str
    
    def __post_init__(self):
        if not self.numero:
            raise ValueError("El número de teléfono es requerido")
        
        # Remover espacios y caracteres especiales para validación
        numero_limpio = self.numero.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        if not numero_limpio.replace("+", "").isdigit():
            raise ValueError("El número de teléfono debe contener solo dígitos")
        
        if len(numero_limpio) < 10:
            raise ValueError("El número de teléfono debe tener al menos 10 dígitos")
