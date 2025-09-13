import datetime
import uuid
from seedwork.dominio.entidades import AgregacionRaiz
import modulos.referidos.dominio.objetos_valor as ov
from dataclasses import dataclass, field
from modulos.referidos.dominio.eventos import ReferidoCreado

@dataclass
class Referido(AgregacionRaiz):
    """Agregado Raíz que representa un referido."""
    idSocio: uuid.UUID = field(hash=True, default=None)
    idReferido: uuid.UUID = field(hash=True, default=None)
    idEvento: uuid.UUID = field(hash=True, default=None)
    monto: float = field(default=0.0)
    estado: ov.EstadoReferido = field(default=ov.EstadoReferido.PENDIENTE)
    fechaEvento: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    tipoEvento: ov.TipoEvento = field(default=ov.TipoEvento.VENTA)
    idEvento: uuid.UUID = field(hash=True, default=None)

    def crear_referido(self, referido: "Referido"):
        self.idSocio = referido.idSocio
        self.idReferido = referido.idReferido
        self.idEvento = referido.idEvento
        self.monto = referido.monto
        self.estado = referido.estado
        self.fechaEvento = referido.fechaEvento
        self.tipoEvento = referido.tipoEvento
        self.idEvento = referido.idEvento


        self.agregar_evento(ReferidoCreado(
            idSocio=self.idSocio,
            idReferido=self.idReferido,
            idEvento=self.idEvento,
            monto=self.monto,
            estado=self.estado,
            fechaEvento=self.fechaEvento,
            fecha_creacion=datetime.datetime.utcnow()
        ))
    