"""Mapeadores para convertir entre objetos de dominio y DTOs de aplicación"""

from typing import List
from .dto import NotificacionDTO
from ..dominio.entidades import Notificacion
from ..dominio.objetos_valor import TipoNotificacion, CanalNotificacion, EstadoNotificacion


class MapeadorNotificacion:
    """Mapeador para convertir entre entidades de Notificación y DTOs"""
    
    @staticmethod
    def entidad_a_dto(notificacion: Notificacion) -> NotificacionDTO:
        """Convierte una entidad Notificación a DTO"""
        return NotificacionDTO(
            id_notificacion=notificacion.id_notificacion,
            id_usuario=notificacion.id_usuario,
            tipo=notificacion.tipo.valor,
            mensaje=notificacion.mensaje,
            canal=notificacion.canal.valor,
            fecha_creacion=notificacion.fecha_creacion,
            estado=notificacion.estado.valor,
            fecha_envio=notificacion.fecha_envio,
            detalle_error=notificacion.detalle_error,
            intentos_envio=notificacion.intentos_envio,
            destinatario=notificacion.destinatario,
            titulo=notificacion.titulo
        )
    
    @staticmethod
    def dto_a_entidad(dto: NotificacionDTO) -> Notificacion:
        """Convierte un DTO a entidad Notificación"""
        # Nota: Usamos el constructor directo en lugar del factory method
        # porque ya tenemos todos los datos, incluyendo ID y fechas
        notificacion = Notificacion(
            id_notificacion=dto.id_notificacion,
            id_usuario=dto.id_usuario,
            tipo=TipoNotificacion(dto.tipo),
            mensaje=dto.mensaje,
            canal=CanalNotificacion(dto.canal),
            fecha_creacion=dto.fecha_creacion,
            estado=EstadoNotificacion(dto.estado),
            fecha_envio=dto.fecha_envio,
            detalle_error=dto.detalle_error,
            intentos_envio=dto.intentos_envio,
            destinatario=dto.destinatario,
            titulo=dto.titulo
        )
        
        # Inicializar la lista de eventos si no existe
        if not hasattr(notificacion, '_eventos'):
            notificacion._eventos = []
        
        return notificacion
    
    @staticmethod
    def entidades_a_dtos(notificaciones: List[Notificacion]) -> List[NotificacionDTO]:
        """Convierte una lista de entidades a DTOs"""
        return [
            MapeadorNotificacion.entidad_a_dto(notificacion)
            for notificacion in notificaciones
        ]
    
    @staticmethod
    def dtos_a_entidades(dtos: List[NotificacionDTO]) -> List[Notificacion]:
        """Convierte una lista de DTOs a entidades"""
        return [
            MapeadorNotificacion.dto_a_entidad(dto)
            for dto in dtos
        ]
