"""
Mapeadores para el módulo de Eventos
"""
from datetime import datetime
import uuid
from modulos.eventos.dominio.objetos_valor import TipoEvento
from modulos.eventos.dominio.entidades import Evento
from seedwork.dominio.repositorios import Mapeador
from .dto import EventoEntity as EventoDTO

class MapeadorEvento(Mapeador):
    _FORMATO_FECHA = '%Y-%m-%dT%H:%M:%SZ'
    def obtener_tipo(self) -> type:
        return Evento.__class__

    def entidad_a_dto(self, entidad: Evento) -> EventoDTO:
        print("DEBUG - Entidad completa:", vars(entidad))  # Imprime todos los atributos de la entidad
        evento_dto = EventoDTO()
        evento_dto.id = str(entidad.id)
        evento_dto.tipo = str(entidad.tipo.value)
        evento_dto.estado = entidad.estado
        evento_dto.id_socio = str(entidad.id_socio)
        evento_dto.id_referido = str(entidad.id_referido)
        evento_dto.monto = entidad.monto
        evento_dto.fecha_creacion = entidad.fecha_creacion
        evento_dto.fecha_evento = entidad.fecha_evento

        return evento_dto

    def dto_a_entidad(self, dto: EventoDTO) -> Evento:
        evento = Evento(
            id=uuid.uuid4(),
            tipo=TipoEvento(dto.tipo),
            id_socio=dto.id_socio,
            id_referido=dto.id_referido,
            monto=dto.monto,
            fecha_creacion=datetime.now(),
            fecha_evento=dto.fecha_evento
        )

        return evento