import datetime
import uuid
from seedwork.dominio.entidades import AgregacionRaiz
from modulos.referidos.dominio.objetos_valor import EstadoReferido, TipoEvento
from dataclasses import dataclass, field, InitVar, InitVar, InitVar, InitVar
from modulos.referidos.dominio.eventos import ReferidoCreado

@dataclass
class Referido(AgregacionRaiz):
    """Agregado Raíz que representa un referido."""
    id: InitVar[uuid.UUID] = None
    idSocio: uuid.UUID = field(hash=True, default=None)
    idReferido: uuid.UUID = field(hash=True, default=None)
    idEvento: uuid.UUID = field(hash=True, default=None)
    monto: float = field(default=0.0)
    estado: EstadoReferido = field(default=EstadoReferido.PENDIENTE)
    fechaEvento: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    tipoEvento: TipoEvento = field(default=TipoEvento.VENTA)

    def __post_init__(self, id: uuid.UUID):
        super().__post_init__(id)

    def crear_referido(self, referido: "Referido"):
        self.idSocio = referido.idSocio
        self.idReferido = referido.idReferido
        self.idEvento = referido.idEvento
        self.monto = referido.monto
        self.estado = EstadoReferido.PENDIENTE
        self.fechaEvento = referido.fechaEvento
        self.tipoEvento = referido.tipoEvento


        self.agregar_evento(ReferidoCreado(
            idSocio=self.idSocio,
            idReferido=self.idReferido,
            idEvento=self.idEvento,
            monto=self.monto,
            estado=self.estado,
            fechaEvento=self.fechaEvento,
            fecha_creacion=datetime.datetime.utcnow()
        ))
    