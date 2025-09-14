# Propósito: Definir los Data Transfer Objects (DTOs) que representan los pagos y sus componentes 
# en la capa de aplicación. Son los objetos que se mueven entre la API y los handlers.

from dataclasses import dataclass, field
from seedwork.aplicacion.dto import DTO

@dataclass(frozen=True)
class EventoPagoDTO(DTO):
    """DTO para la entidad de EventoPago."""
    id: str = field(default_factory=str)
    tipoEvento: str = field(default_factory=str)
    idUsuario: str = field(default_factory=str)
    detalles: str = field(default_factory=str)
    fechaEvento: str = field(default_factory=str)

@dataclass(frozen=True)
class ReferidoDTO(DTO):
    """DTO para la entidad de Referido."""
    id: str = field(default_factory=str)
    idSocio: str = field(default_factory=str)
    idReferido: str = field(default_factory=str)
    monto: str = field(default_factory=str)
    estado: str = field(default_factory=str)
    idEvento: str = field(default_factory=str)
    fechaEvento: str = field(default_factory=str)
    tipoEvento: str = field(default_factory=str)
    fecha_creacion: str = field(default_factory=str)
    fecha_actualizacion: str = field(default_factory=str)