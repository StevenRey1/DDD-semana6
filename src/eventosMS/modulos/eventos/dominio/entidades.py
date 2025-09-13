"""
Entidades del dominio de Eventos
"""
from __future__ import annotations
from dataclasses import dataclass, field
from seedwork.dominio.entidades import AgregacionRaiz
from .objetos_valor import TipoEvento
from .eventos import EventoRegistrado
from datetime import datetime
from uuid import UUID
from typing import Optional


@dataclass
class Evento(AgregacionRaiz):
    """
    Entidad principal que representa un evento en el sistema
    """
    id: UUID = field(default=None)
    tipo: TipoEvento = field(default=None)
    id_socio: UUID = field(default=None)
    id_referido: Optional[UUID] = field(default=None)
    monto: float = field(default=0.0)
    ganancia: float = field(default=0.0)
    estado: str = field(default="pendiente")
    fecha_evento: datetime = field(default=None)

    def crear_evento(self, evento: Evento):
        """
        Método para iniciar la creación del agregado.
        Dispara el evento de dominio inicial.
        """
        self.tipo = evento.tipo
        self.id_socio = evento.id_socio
        self.id_referido = evento.id_referido
        self.monto = evento.monto
        self.ganancia = evento.ganancia
        self.estado = evento.estado
        self.fecha_creacion = evento.fecha_creacion
        self.fecha_actualizacion = evento.fecha_actualizacion
        self.fecha_evento = evento.fecha_evento

        self.agregar_evento(EventoRegistrado(
            evento_id=self.id,
            tipo_evento=self.tipo.valor,
            id_referido=self.id_referido,
            id_socio=self.id_socio,
            monto=self.monto,
            ganancia=self.ganancia,
            estado=self.estado,
            fecha_evento=self.fecha_evento
        ))
