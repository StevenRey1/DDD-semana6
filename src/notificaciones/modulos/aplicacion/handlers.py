"""Registro central de todos los handlers de comandos y queries"""

from typing import Dict, Type, Any

from .comandos.base import ComandoHandler, Comando
from .comandos.crear_notificacion import (
    ComandoCrearNotificacion, ComandoCrearNotificacionHandler,
    ComandoEnviarNotificacion, ComandoEnviarNotificacionHandler,
    ComandoMarcarNotificacionFallida, ComandoMarcarNotificacionFallidaHandler
)

from .queries.base import QueryHandler, Query
from .queries.obtener_notificaciones import (
    ObtenerNotificacionPorId, ObtenerNotificacionPorIdHandler,
    ObtenerNotificacionesPorUsuario, ObtenerNotificacionesPorUsuarioHandler,
    ObtenerNotificacionesPendientes, ObtenerNotificacionesPendientesHandler,
    ObtenerTodasNotificaciones, ObtenerTodasNotificacionesHandler
)

from ..dominio.repositorios import RepositorioNotificaciones
from ..infraestructura.despachadores import DespachadorEventos


class RegistroHandlers:
    """Registro central de handlers para inyección de dependencias"""
    
    def __init__(
        self,
        repositorio_notificaciones: RepositorioNotificaciones,
        despachador_eventos: DespachadorEventos
    ):
        self.repositorio_notificaciones = repositorio_notificaciones
        self.despachador_eventos = despachador_eventos
        
        # Registros de handlers
        self._comando_handlers: Dict[Type[Comando], ComandoHandler] = {}
        self._query_handlers: Dict[Type[Query], QueryHandler] = {}
        
        # Registrar todos los handlers
        self._registrar_comando_handlers()
        self._registrar_query_handlers()
    
    def _registrar_comando_handlers(self):
        """Registra todos los handlers de comandos"""
        self._comando_handlers[ComandoCrearNotificacion] = ComandoCrearNotificacionHandler(
            self.repositorio_notificaciones,
            self.despachador_eventos
        )
        
        self._comando_handlers[ComandoEnviarNotificacion] = ComandoEnviarNotificacionHandler(
            self.repositorio_notificaciones,
            self.despachador_eventos
        )
        
        self._comando_handlers[ComandoMarcarNotificacionFallida] = ComandoMarcarNotificacionFallidaHandler(
            self.repositorio_notificaciones,
            self.despachador_eventos
        )
    
    def _registrar_query_handlers(self):
        """Registra todos los handlers de queries"""
        self._query_handlers[ObtenerNotificacionPorId] = ObtenerNotificacionPorIdHandler(
            self.repositorio_notificaciones
        )
        
        self._query_handlers[ObtenerNotificacionesPorUsuario] = ObtenerNotificacionesPorUsuarioHandler(
            self.repositorio_notificaciones
        )
        
        self._query_handlers[ObtenerNotificacionesPendientes] = ObtenerNotificacionesPendientesHandler(
            self.repositorio_notificaciones
        )
        
        self._query_handlers[ObtenerTodasNotificaciones] = ObtenerTodasNotificacionesHandler(
            self.repositorio_notificaciones
        )
    
    def obtener_comando_handler(self, comando_type: Type[Comando]) -> ComandoHandler:
        """Obtiene el handler para un tipo de comando"""
        handler = self._comando_handlers.get(comando_type)
        if not handler:
            raise ValueError(f"No se encontró handler para comando {comando_type.__name__}")
        return handler
    
    def obtener_query_handler(self, query_type: Type[Query]) -> QueryHandler:
        """Obtiene el handler para un tipo de query"""
        handler = self._query_handlers.get(query_type)
        if not handler:
            raise ValueError(f"No se encontró handler para query {query_type.__name__}")
        return handler
    
    async def ejecutar_comando(self, comando: Comando) -> Any:
        """Ejecuta un comando usando su handler correspondiente"""
        handler = self.obtener_comando_handler(type(comando))
        return await handler.handle(comando)
    
    async def ejecutar_query(self, query: Query) -> Any:
        """Ejecuta una query usando su handler correspondiente"""
        handler = self.obtener_query_handler(type(query))
        return await handler.handle(query)
