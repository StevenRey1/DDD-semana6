from dataclasses import dataclass
from typing import Optional, List

from .base import Query, QueryHandler
from ..dto import NotificacionDTO, ListaNotificacionesDTO, EstadisticasNotificacionesDTO
from ..mapeadores import MapeadorNotificacion
from ...dominio.repositorios import RepositorioNotificaciones


@dataclass
class ObtenerNotificacionPorId(Query):
    """Query para obtener una notificación por ID"""
    id_notificacion: str


class ManejadorObtenerNotificacion(QueryHandler):
    """Handler para obtener una notificación por ID"""
    
    def __init__(self, repositorio_notificaciones: RepositorioNotificaciones):
        self.repositorio_notificaciones = repositorio_notificaciones
    
    async def handle(self, query: ObtenerNotificacionPorId) -> Optional[NotificacionDTO]:
        """Obtiene una notificación por su ID"""
        notificacion = await self.repositorio_notificaciones.obtener_por_id(query.id_notificacion)
        
        if not notificacion:
            return None
        
        return MapeadorNotificacion.entidad_a_dto(notificacion)


@dataclass
class ObtenerNotificacionesPorUsuario(Query):
    """Query para obtener notificaciones de un usuario"""
    id_usuario: str
    limite: int = 50
    offset: int = 0


class ManejadorObtenerNotificacionesPorUsuario(QueryHandler):
    """Handler para obtener notificaciones por usuario"""
    
    def __init__(self, repositorio_notificaciones: RepositorioNotificaciones):
        self.repositorio_notificaciones = repositorio_notificaciones
    
    async def handle(self, query: ObtenerNotificacionesPorUsuario) -> ListaNotificacionesDTO:
        """Obtiene todas las notificaciones de un usuario"""
        notificaciones = await self.repositorio_notificaciones.obtener_por_usuario(query.id_usuario)
        total = await self.repositorio_notificaciones.contar_por_usuario(query.id_usuario)
        
        # Aplicar paginación manualmente (en una implementación real esto se haría en el repositorio)
        notificaciones_paginadas = notificaciones[query.offset:query.offset + query.limite]
        
        notificaciones_dto = [
            MapeadorNotificacion.entidad_a_dto(notif) 
            for notif in notificaciones_paginadas
        ]
        
        return ListaNotificacionesDTO(
            notificaciones=notificaciones_dto,
            total=total,
            pagina=query.offset // query.limite + 1,
            limite=query.limite
        )


@dataclass
class ObtenerNotificacionesPendientes(Query):
    """Query para obtener notificaciones pendientes"""
    limite: int = 100


class ManejadorObtenerNotificacionesPendientes(QueryHandler):
    """Handler para obtener notificaciones pendientes"""
    
    def __init__(self, repositorio_notificaciones: RepositorioNotificaciones):
        self.repositorio_notificaciones = repositorio_notificaciones
    
    async def handle(self, query: ObtenerNotificacionesPendientes) -> List[NotificacionDTO]:
        """Obtiene todas las notificaciones pendientes"""
        notificaciones = await self.repositorio_notificaciones.obtener_pendientes()
        
        # Limitar resultados
        notificaciones_limitadas = notificaciones[:query.limite]
        
        return [
            MapeadorNotificacion.entidad_a_dto(notif) 
            for notif in notificaciones_limitadas
        ]


@dataclass
class ObtenerTodasNotificaciones(Query):
    """Query para obtener todas las notificaciones con paginación"""
    limite: int = 50
    offset: int = 0


class ObtenerTodasNotificacionesHandler(QueryHandler):
    """Handler para obtener todas las notificaciones"""
    
    def __init__(self, repositorio_notificaciones: RepositorioNotificaciones):
        self.repositorio_notificaciones = repositorio_notificaciones
    
    async def handle(self, query: ObtenerTodasNotificaciones) -> ListaNotificacionesDTO:
        """Obtiene todas las notificaciones con paginación"""
        notificaciones = await self.repositorio_notificaciones.obtener_todas(
            limite=query.limite,
            offset=query.offset
        )
        
        # Para el total, necesitaríamos otra query o método en el repositorio
        # Por simplicidad, usamos len de todas las notificaciones
        todas_notificaciones = await self.repositorio_notificaciones.obtener_todas(limite=10000)
        total = len(todas_notificaciones)
        
        notificaciones_dto = [
            MapeadorNotificacion.entidad_a_dto(notif) 
            for notif in notificaciones
        ]
        
        return ListaNotificacionesDTO(
            notificaciones=notificaciones_dto,
            total=total,
            pagina=query.offset // query.limite + 1,
            limite=query.limite
        )


@dataclass
class ConsultaObtenerEstadisticasNotificaciones(Query):
    """Consulta para obtener estadísticas de notificaciones"""
    pass


class ManejadorObtenerEstadisticasNotificaciones(QueryHandler):
    """Handler para obtener estadísticas de notificaciones"""
    
    def __init__(self, repositorio_notificaciones: RepositorioNotificaciones):
        self.repositorio_notificaciones = repositorio_notificaciones
    
    async def handle(self, query: ConsultaObtenerEstadisticasNotificaciones) -> EstadisticasNotificacionesDTO:
        """Obtiene estadísticas completas de notificaciones"""
        
        # Obtener todas las notificaciones
        todas = await self.repositorio_notificaciones.obtener_todas()
        
        # Calcular estadísticas
        total = len(todas)
        
        # Por estado
        por_estado = {}
        for notif in todas:
            estado = notif.estado.valor
            por_estado[estado] = por_estado.get(estado, 0) + 1
        
        # Por tipo
        por_tipo = {}
        for notif in todas:
            tipo = notif.tipo.valor
            por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
        
        # Por canal
        por_canal = {}
        for notif in todas:
            canal = notif.canal.valor
            por_canal[canal] = por_canal.get(canal, 0) + 1
        
        return EstadisticasNotificacionesDTO(
            total_notificaciones=total,
            pendientes=por_estado.get("pendiente", 0),
            enviadas=por_estado.get("enviada", 0),
            fallidas=por_estado.get("fallida", 0),
            canceladas=por_estado.get("cancelada", 0),
            por_tipo=por_tipo,
            por_canal=por_canal
        )
