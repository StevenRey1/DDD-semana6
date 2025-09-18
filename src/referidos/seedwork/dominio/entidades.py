"""Entidades reusables parte del seedwork del proyecto

En este archivo usted encontrará las entidades reusables parte del seedwork del proyecto

"""

from dataclasses import dataclass, field
from .eventos import EventoDominio
from .mixins import ValidarReglasMixin
from .reglas import IdEntidadEsInmutable
from .excepciones import IdDebeSerInmutableExcepcion
from datetime import datetime
import uuid

@dataclass
class Entidad:
    _id: uuid.UUID = field(init=False, repr=False, hash=True)
    fecha_creacion: datetime =  field(default_factory=datetime.now)
    fecha_actualizacion: datetime = field(default_factory=datetime.now)

    def __post_init__(self, id: uuid.UUID = None):
        if id is not None:
            self._id = id
        elif not hasattr(self, '_id') or self._id is None:
            self._id = self.siguiente_id()

    @classmethod
    def siguiente_id(self) -> uuid.UUID:
        return uuid.uuid4()

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value: uuid.UUID) -> None:
        if not hasattr(self, '_id') or self._id is None:
            self._id = value
        elif self._id != value:
            raise IdDebeSerInmutableExcepcion()
        

@dataclass
class AgregacionRaiz(Entidad, ValidarReglasMixin):
    eventos: list[EventoDominio] = field(default_factory=list)

    def __post_init__(self, id: uuid.UUID = None):
        super().__post_init__(id=id)

    def agregar_evento(self, evento: EventoDominio):
        self.eventos.append(evento)
    
    def limpiar_eventos(self):
        self.eventos = list()


@dataclass
class Locacion(Entidad):
    def __str__(self) -> str:
        ...