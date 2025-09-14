import uuid
from seedwork.dominio.entidades import AgregacionRaiz
from dataclasses import dataclass, field

@dataclass
class Referido(AgregacionRaiz):
    id_socio: uuid.UUID = field(hash=True, default=None)
    id_evento: uuid.UUID = field(default=None)
    tipo_evento: str = field(default=None)
    id_referido: uuid.UUID = field(default=None)
    monto: float = field(default=None)
    estado: str = field(default=None)
    fecha_evento: str = field(default=None)