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
        evento_dto = EventoDTO()
        evento_dto.id = str(entidad.id)
        evento_dto.tipo = str(entidad.tipo.value)
        evento_dto.estado = entidad.estado
        evento_dto.id_socio = str(entidad.id_socio)
        evento_dto.id_referido = str(entidad.id_referido)
        evento_dto.monto = entidad.monto
        evento_dto.ganancia = entidad.ganancia  # Incluir ganancia
        evento_dto.fecha_creacion = entidad.fecha_creacion
        evento_dto.fecha_evento = entidad.fecha_evento

        return evento_dto

    def dto_a_entidad(self, dto: EventoDTO) -> Evento:
        if hasattr(dto, 'id') and dto.id:
            if isinstance(dto.id, uuid.UUID):
                evento_id = dto.id
            else:
                evento_id = uuid.UUID(dto.id)
        else:
            evento_id = uuid.uuid4()

        
        if hasattr(dto, 'ganancia') and dto.ganancia:
            ganancia = dto.ganancia
        else:
            ganancia = 0

        if hasattr(dto, 'estado') and dto.estado:
            estado = dto.estado
        else:
            estado = "pendiente"

        evento = Evento(
            id=evento_id,
            tipo=TipoEvento(dto.tipo),
            id_socio=dto.id_socio,
            id_referido=dto.id_referido,
            monto=dto.monto,
            fecha_creacion=datetime.now(),
            fecha_evento=dto.fecha_evento,
            ganancia=ganancia,
            estado=estado
        )

        return evento

    def update_dto_a_entidad(self, dto: EventoDTO) -> Evento:
        evento = Evento(
            id=dto.id,
            tipo=TipoEvento(dto.tipo),
            id_socio=dto.id_socio,
            id_referido=dto.id_referido,
            monto=dto.monto,
            fecha_creacion=dto.fecha_creacion,
            fecha_evento=dto.fecha_evento,
            ganancia=dto.ganancia,  # Solo campos existentes
            estado=dto.estado
        )

        return evento

    def update_entidad_a_dto(self, evento: Evento) -> EventoDTO:
        evento_dto = EventoDTO()
        evento_dto.id = evento.id  # Mantener como UUID, no como string para la actualización
        evento_dto.tipo = str(evento.tipo.value)
        evento_dto.estado = evento.estado
        evento_dto.id_socio = evento.id_socio  # Mantener como UUID
        evento_dto.id_referido = evento.id_referido  # Mantener como UUID
        evento_dto.monto = evento.monto
        evento_dto.ganancia = evento.ganancia  # ¡IMPORTANTE! Incluir ganancia actualizada
        evento_dto.fecha_creacion = evento.fecha_creacion
        evento_dto.fecha_evento = evento.fecha_evento

        return evento_dto