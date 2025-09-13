"""Servicios de aplicación para notificaciones"""

from typing import List, Optional
from datetime import datetime

from ..dominio.repositorios import RepositorioNotificaciones
from ..dominio.entidades import Notificacion
from ..dominio.fabricas import FabricaNotificaciones
from ..infraestructura.despachadores import DespachadorEventos
from .dto import (
    NotificacionDTO, 
    CrearNotificacionDTO, 
    ListaNotificacionesDTO,
    EstadisticasNotificacionesDTO
)
from .mapeadores import MapeadorNotificacion
from .comandos.crear_notificacion import (
    ComandoCrearNotificacion,
    ComandoEnviarNotificacion, 
    ComandoMarcarNotificacionFallida,
    ManejadorCrearNotificacion,
    ManejadorEnviarNotificacion,
    ManejadorMarcarNotificacionFallida
)
from .queries.obtener_notificaciones import (
    ObtenerTodasNotificaciones,
    ObtenerTodasNotificacionesHandler,
    ConsultaObtenerEstadisticasNotificaciones,
    ManejadorObtenerEstadisticasNotificaciones
)


class ServicioAplicacionNotificaciones:
    """Servicio de aplicación para coordinar operaciones de notificaciones"""
    
    def __init__(
        self,
        repositorio: RepositorioNotificaciones,
        despachador_eventos: DespachadorEventos
    ):
        self.repositorio = repositorio
        self.despachador_eventos = despachador_eventos
        self.mapeador = MapeadorNotificacion()
        
        # Inicializar manejadores de comandos
        self.manejador_crear = ManejadorCrearNotificacion(repositorio, despachador_eventos)
        self.manejador_enviar = ManejadorEnviarNotificacion(repositorio, despachador_eventos)
        self.manejador_marcar_fallida = ManejadorMarcarNotificacionFallida(repositorio, despachador_eventos)
        
        # Inicializar manejadores de consultas
        self.manejador_obtener = ObtenerTodasNotificacionesHandler(repositorio)
        self.manejador_estadisticas = ManejadorObtenerEstadisticasNotificaciones(repositorio)
    
    # Comandos
    
    async def crear_notificacion(self, dto: CrearNotificacionDTO) -> NotificacionDTO:
        """Crea una nueva notificación"""
        comando = ComandoCrearNotificacion(
            id_usuario=dto.id_usuario,
            tipo=dto.tipo,
            canal=dto.canal,
            destinatario=dto.destinatario,
            titulo=dto.titulo,
            mensaje=dto.mensaje,
            datos_adicionales=dto.datos_adicionales
        )
        
        notificacion = await self.manejador_crear.handle(comando)
        return self.mapeador.entidad_a_dto(notificacion)
    
    async def enviar_notificacion(self, id_notificacion: str) -> NotificacionDTO:
        """Envía una notificación pendiente"""
        comando = ComandoEnviarNotificacion(id_notificacion=id_notificacion)
        notificacion = await self.manejador_enviar.handle(comando)
        return self.mapeador.entidad_a_dto(notificacion)
    
    async def marcar_notificacion_fallida(self, id_notificacion: str, error: str) -> NotificacionDTO:
        """Marca una notificación como fallida"""
        comando = ComandoMarcarNotificacionFallida(
            id_notificacion=id_notificacion,
            detalle_error=error
        )
        notificacion = await self.manejador_marcar_fallida.handle(comando)
        return self.mapeador.entidad_a_dto(notificacion)
    
    # Consultas
    
    async def obtener_notificacion(self, id_notificacion: str) -> Optional[NotificacionDTO]:
        """Obtiene una notificación por su ID"""
        notificacion = await self.repositorio.obtener_por_id(id_notificacion)
        
        if notificacion:
            return self.mapeador.entidad_a_dto(notificacion)
        return None
    
    async def obtener_notificaciones_usuario(
        self, 
        id_usuario: str, 
        limite: int = 50, 
        offset: int = 0
    ) -> ListaNotificacionesDTO:
        """Obtiene las notificaciones de un usuario"""
        # Usar repository directamente por ahora
        notificaciones = await self.repositorio.obtener_por_usuario(id_usuario, limite, offset)
        total = await self.repositorio.contar_por_usuario(id_usuario)
        
        items = [self.mapeador.entidad_a_dto(notif) for notif in notificaciones]
        
        return ListaNotificacionesDTO(
            notificaciones=items,
            total=total,
            pagina=offset // limite if limite > 0 else 0,
            limite=limite
        )
    
    async def obtener_notificaciones_pendientes(self) -> List[NotificacionDTO]:
        """Obtiene todas las notificaciones pendientes"""
        notificaciones = await self.repositorio.obtener_pendientes()
        
        return [self.mapeador.entidad_a_dto(notif) for notif in notificaciones]
    
    async def obtener_estadisticas(self) -> EstadisticasNotificacionesDTO:
        """Obtiene estadísticas de notificaciones"""
        consulta = ConsultaObtenerEstadisticasNotificaciones()
        return await self.manejador_estadisticas.handle(consulta)
    
    # Métodos auxiliares
    
    async def procesar_notificaciones_pendientes(self) -> int:
        """Procesa todas las notificaciones pendientes y retorna el número procesado"""
        notificaciones_dto = await self.obtener_notificaciones_pendientes()
        procesadas = 0
        
        for notificacion_dto in notificaciones_dto:
            try:
                await self.enviar_notificacion(notificacion_dto.id_notificacion)
                procesadas += 1
            except Exception as e:
                # Marcar como fallida si hay error
                await self.marcar_notificacion_fallida(
                    notificacion_dto.id_notificacion,
                    str(e)
                )
        
        return procesadas
